<?php
/**
 * Created by PhpStorm.
 * User: Sebastian Schüpbach
 * Date: 03.06.15
 * Time: 10:58
 */

require 'vendor/autoload.php';

class esQuery {

    function __construct($connections, $index, $type) {

        // Create client
        $client = new Elastica\Client();

        // Define connections to node. Seems a bit verbose, but if we choose the way described on
        // http://elastica.io/getting-started/installation.html it will throw an error
        foreach($connections as $host => $port) {
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
     * @param array $field
     * @return \Elastica\Query\Match
     */
    protected function createMatchFrag($field = array()) {
        $frag = new Elastica\Query\Match();
        $frag->setField(array_keys($field)[0], $field[array_keys($field)[0]]);
        return $frag;
    }


    /**
     * @param array $field
     * @return \Elastica\Query\Range
     */
    protected function createRangeFrag($field = array()) {
        $frag = new Elastica\Query\Range();
        $frag->addField(array_keys($field)[0], $field[array_keys($field)[0]]);
        return $frag;
    }


    /**
     * @param array $field
     * @return \Elastica\Query\Term
     */
    protected function createTermFrag($field = array()) {
        $frag = new Elastica\Query\Term();
        $frag->setTerm(array_keys($field)[0], $field[array_keys($field)[0]]);
        return $frag;
    }


    /**
     * @param $qtype
     * @param $field
     * @return \Elastica\Query\Match|\Elastica\Query\Range|\Elastica\Query\Term|null
     */
    protected function createFrag($qtype, $field) {
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
     * @param $nested
     * @param $qtype
     * @param array $field
     * @return \Elastica\Query\Match|\Elastica\Query\Nested|\Elastica\Query\Range|\Elastica\Query\Term
     */
    protected function createNestedFrag($nested, $qtype, $field = array()) {
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
     * @param $bool
     * @param bool $nested
     * @param $qtype
     * @param $field
     */
    public function add($bool, $nested = false, $qtype, $field) {
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
     * @param $limit
     */
    public function search($limit) {
        $this->query->setQuery($this->body);
        $this->resultSet = $this->search->search($this->query, $limit);
    }


    public function tojsonld() {
        $results = array();
        foreach($this->resultSet->getResults() as $doc) {
            //var_dump($doc);
            $result = $doc->getData();
            $context = (object)$result['@context'];
            unset($result['@context']);
            $results[] = jsonld_compact((object)$result, $context);
//            $results[] = json_encode($result,
//                JSON_UNESCAPED_SLASHES |
//                // JSON_PRETTY_PRINT |
//                JSON_UNESCAPED_UNICODE);
        }
        return $results;
    }


    public function tottl() {
        // Todo: Should we use EasyRDF to convert from Nquads to Turtle?
    }

    public function tonquads() {
        // Todo: Blank nodes should be recreated instead of just being "dropped"
        return jsonld_normalize($this->tojsonld(), array('format' => 'application/nquads'));
    }

    public function tordfa() {
        // Todo: Should we use EasyRDF to convert from Nquads to RDFa?
    }
}

// Just a small example. Replace <hostX>, <portX>, <index> and <type> with the respective nodes, index and type of ES
$test = new esQuery([
    '<host1>' => <port1>,
    '<host2>' => <port2>,
    '<port1>' => <port3>], '<index>', '<type>');
// $test->add('or', false, 'match', ['dct:title' => 'test']);
// $test->add('or', true, 'match', ['foaf:firstName' => 'John']);
// $test->add('and', false, 'range', ['dct:issued' => ['from' => '1900', 'to' => '2010']]);
$test->add('and', false, 'match', ['_all' => 'Carl']);
$test->add('not', false, 'match', ['dct:title' => 'Carl']);
$test->search(50);
//$test->tojsonld();
print_r($test->tonquads());