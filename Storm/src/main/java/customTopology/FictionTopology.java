package customTopology;
import backtype.storm.Config;
import backtype.storm.LocalCluster;
import backtype.storm.task.TopologyContext;
import backtype.storm.topology.BasicOutputCollector;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.base.BaseBasicBolt;
import backtype.storm.tuple.Fields;
import backtype.storm.tuple.Tuple;
import backtype.storm.utils.Utils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import storm.kafka.BrokerHosts;
import storm.kafka.KafkaSpout;
import storm.kafka.SpoutConfig;
import storm.kafka.ZkHosts;

import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

import storm.trident.TridentTopology;
import storm.kafka.trident.TridentKafkaConfig;
import backtype.storm.spout.SchemeAsMultiScheme;
import storm.kafka.StringScheme;
import storm.kafka.trident.OpaqueTridentKafkaSpout;
import java.io.IOException;
import customStreams.print;
//import org.apache.log4j.Log4jLoggerFactory;
/**
 * Created by gxkj-941 on 2017/4/1.
 */
public class FictionTopology {
    public static final String FUNCTION_QUEUE = "TEMP_FUNCTION_QUEUE2";
    private SpoutConfig spoutConf = null;
    private KafkaSpout kafkaspout = null;
    FictionTopology(String brokerZkStr, String topic, String zkRoot, String id){
        spoutConf = new SpoutConfig(new ZkHosts(brokerZkStr),topic,zkRoot,id);
        kafkaspout = new KafkaSpout(spoutConf);
    }

    public static void main(String args[]) throws IOException{
//        FictionTopology ft = new FictionTopology("gx.master:2181", FUNCTION_QUEUE,"/brokers/topics","0");
//        TopologyBuilder builder = new TopologyBuilder();
        TridentTopology topology = new TridentTopology();
        Properties prop = new Properties();
        InputStream ins = FictionTopology.class.getResourceAsStream("../stormSettings.properties");
        prop.load(ins);
        BrokerHosts zk = new ZkHosts(prop.getProperty("storm.zookeeper.address"));
        TridentKafkaConfig spoutConf = new TridentKafkaConfig(zk, FUNCTION_QUEUE);
        spoutConf.scheme = new SchemeAsMultiScheme(new StringScheme());
        OpaqueTridentKafkaSpout spout = new OpaqueTridentKafkaSpout(spoutConf);
        Fields f = spout.getOutputFields();
        topology.newStream("a",spout).each( f, new print(), new Fields("word"));
//        topology.setBolt("2", new exampleBolt());

        Map conf = new HashMap();
        conf.put(Config.TOPOLOGY_WORKERS, 4);
        conf.put("enable.auto.commit", "true");
        conf.put("auto.commit.interval.ms", "1000");
        conf.put("group.id", "test1");
        try {
//               StormSubmitter.submitTopology("mytopology", conf, builder.createTopology());
            LocalCluster cluster = new LocalCluster(prop.getProperty("storm.nimbus.host"), Long.valueOf(prop.getProperty("storm.zookeeper.port")));
//               cluster.submitTopologyWithOpts();
            cluster.submitTopology("mytopology", conf,topology.build());
//            Utils.sleep(10000);
//            cluster.shutdown();
        }
        catch(Exception e){
            e.printStackTrace();
        }
    }
}





