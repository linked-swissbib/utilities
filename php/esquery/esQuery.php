<?php
/**
 * Created by PhpStorm.
 * User: Sebastian Schüpbach
 * Date: 03.06.15
 * Time: 10:58
 */

require 'vendor/autoload.php';

class esQuery
{
    /**
     * @param array $connections: Connections to Elasticsearch nodes as host => port pairs
     * @param string $index: Name of Elasticsearch index
     * @param string $type: Name of Elasticsearch type
     */
    function __construct($connections, $index, $type)
    {

        // Create client
        $client = new Elastica\Client();

        // Define connections to node. Seems a bit verbose, but if we chose the way described on
        // http://elastica.io/getting-started/installation.html it crashed
        foreach ($connections as $host => $port) {
            $connobj = new Elastica\Connection();
            $connobj->setHost($host);
            $connobj->setPort($port);
            $client->addConnection($connobj);
        }

        // Create search object
        $this->search = new Elastica\Search($client);
        $this->search->addIndex($index);
        $this->search->addType($type);

        // Create query object
        $this->query = new Elastica\Query();

        // Create query body object
        $this->body = new Elastica\Query\Bool();
        $this->body->setMinimumNumberShouldMatch(1);

        $this->resultSet = array();
    }


    /**
     * Creates a match query fragment
     * @param array $field: Field name and value as field => value
     * @return \Elastica\Query\Match
     */
    protected function createMatchFrag($field = array())
    {
        $frag = new Elastica\Query\Match();
        $frag->setField(array_keys($field)[0], $field[array_keys($field)[0]]);
        return $frag;
    }


    /**
     * Creates a range query fragment
     * @param array $field: Field name and value as field => value
     * @return \Elastica\Query\Range
     */
    protected function createRangeFrag($field = array())
    {
        $frag = new Elastica\Query\Range();
        $frag->addField(array_keys($field)[0], $field[array_keys($field)[0]]);
        return $frag;
    }


    /**
     * Creates a term query fragment
     * @param array $field: Field name and value as field => value
     * @return \Elastica\Query\Term
     */
    protected function createTermFrag($field = array())
    {
        $frag = new Elastica\Query\Term();
        $frag->setTerm(array_keys($field)[0], $field[array_keys($field)[0]]);
        return $frag;
    }


    /**
     * Creates an enwrapping bool query fragment
     * @param string $qtype: Type of query. Possible values are 'match', 'range' and 'term'
     * @param $field: Field name and value as field => value
     * @return \Elastica\Query\Match|\Elastica\Query\Range|\Elastica\Query\Term|null
     */
    protected function createFrag($qtype, $field)
    {
        switch ($qtype) {
            case 'match':
                $frag = $this->createMatchFrag($field);
                break;
            case 'range':
                $frag = $this->createRangeFrag($field);
                break;
            case 'term':
                $frag = $this->createTermFrag($field);
                break;
            default:
                $frag = Null;
        }
        return $frag;
    }


    /**
     * Wraps query fragment as nested query if nested=true
     * @param bool $nested: Build as nested query element (i.e. look for field value in dc:contributor)
     * @param string $qtype: Type of query. Possible values are 'match', 'range' and 'term'
     * @param array $field: Field name and value as field => value
     * @return \Elastica\Query\Match|\Elastica\Query\Nested|\Elastica\Query\Range|\Elastica\Query\Term
     */
    protected function createNestedFrag($nested, $qtype, $field = array())
    {
        if ($nested) {
            $wrapper = new Elastica\Query\Nested();
            $wrapper->setPath('dc:contributor');
            $wrapper->setQuery($this->createFrag($qtype, $field));
        } else {
            $wrapper = $this->createFrag($qtype, $field);
        }
        return $wrapper;
    }


    /**
     * Add a query element
     * @param string $bool: Logical connective. Possible values are 'and', 'or' and 'not'
     * @param bool $nested: Build as nested query element (i.e. look for field value in dc:contributor)
     * @param string $qtype: Type of query. Possible values are 'match', 'range' and 'term'
     * @param array $field: Field name and value as field => value
     */
    public function add($bool, $nested = false, $qtype, $field)
    {
        switch ($bool) {
            case 'and':
                $this->body->addMust($this->createNestedFrag($nested, $qtype, $field));
                break;
            case 'or':
                $this->body->addShould($this->createNestedFrag($nested, $qtype, $field));
                break;
            case 'not':
                $this->body->addMustNot($this->createNestedFrag($nested, $qtype, $field));
                break;
        }
    }


    /**
     * Performs query
     * @param int $limit: Max search results
     */
    public function search($limit)
    {
        $this->query->setQuery($this->body);
        $this->resultSet = $this->search->search($this->query, $limit);
    }


    /**
     * Converts query results to flattened JSON-LD objects
     * @return array: Array with the flattened JSON-LD objects of the results
     */
    public function tojsonld()
    {
        $results = array();
        foreach ($this->resultSet->getResults() as $doc) {
            $result = $doc->getData();
            $context = (object)$result['@context'];
            unset($result['@context']);
            $bnodes = $result['dc:contributor'];
            unset($result['dc:contributor']);
            $graph = array();
            foreach ($bnodes as $bnode) {
                $graph[] = $bnode;
                $graph[] = $bnode;
                $result['dc:contributor'][] = $bnode['@id'];
            }
            $graph[] = $result;
            $results[] = jsonld_flatten(json_decode(json_encode($graph), FALSE), $context);
        }
        return $results;
    }


    /**
     * Loads JSON-Documents into an graph object
     * @param object $doc : Document to be loaded
     * @return EasyRdf_Graph
     */
    protected function json2rdf($doc)
    {
        $graph = new EasyRdf_Graph();
        $result = $doc->getData();
        $result = json_decode(json_encode($result));
        $rdf = json_decode(json_encode(jsonld_to_rdf($result, FALSE)), TRUE);
        foreach ($rdf['@default'] as $triple) {
            switch ($triple['object']['type']) {
                case 'literal':
                    $graph->addLiteral($triple['subject']['value'],
                        $triple['predicate']['value'],
                        $triple['object']['value']);
                    break;
                case 'IRI':
                    $graph->addResource($triple['subject']['value'],
                        $triple['predicate']['value'],
                        $triple['object']['value']);
                    break;
                case 'blank node':
                    $graph->addResource($triple['subject']['value'],
                        $triple['predicate']['value'],
                        $triple['object']['value']);
            }
        }
        return $graph;
    }


    /**
     * Serialise RDF-Graph into a specified format
     * @param string $format : Target format. Possible values are:
     * json, jsonld (with ml/json-ld installed), n3, ntriples, rdfxml, turtle; php (Array); dot; gif, png, svg
     * @return array: Array containing the serialised documents
     */
    public function serialise($format)
    {
        $bag = array();
        foreach ($this->resultSet->getResults() as $doc) {
            $graph = $this->json2rdf($doc);
            $bag[] = $graph->serialise($format);
        }
        return $bag;
    }


    public function tonquads()
    {
        //return jsonld_expand($this->tojsonld());
        return jsonld_normalize(jsonld_expand($this->tojsonld()), array('format' => 'application/nquads'));
    }

}