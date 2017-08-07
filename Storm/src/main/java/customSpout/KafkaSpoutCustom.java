package customSpout;

//
//import org.apache.storm.starter.spout.RandomSentenceSpout;
//import org.apache.storm.task.ShellBolt;
//import org.apache.storm.topology.BasicOutputCollector;
//import org.apache.storm.topology.ConfigurableTopology;
//import org.apache.storm.topology.IRichBolt;
//import org.apache.storm.topology.OutputFieldsDeclarer;
//import org.apache.storm.topology.TopologyBuilder;
//import org.apache.storm.topology.base.BaseBasicBolt;
//import org.apache.storm.tuple.Fields;
//import org.apache.storm.tuple.Tuple;
//import org.apache.storm.tuple.Values;

import storm.kafka.SpoutConfig;
import storm.kafka.KafkaSpout;
import storm.kafka.BrokerHosts;
/**
 * Created by gxkj-941 on 2017/3/31.
 */
public class KafkaSpoutCustom   {
    private SpoutConfig spconfig = null;
    private KafkaSpout kafkaSpout = null;
    public KafkaSpoutCustom(BrokerHosts hosts, String topic, String zkRoot, String id){
        spconfig = new SpoutConfig(hosts, topic, zkRoot, id);
        kafkaSpout = new KafkaSpout(spconfig);
    }

}
