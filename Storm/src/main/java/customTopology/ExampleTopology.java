package customTopology;

import java.util.HashMap;
import java.util.Map;

import backtype.storm.topology.TopologyBuilder;
import backtype.storm.testing.TestWordSpout;
import backtype.storm.testing.TestWordCounter;
import backtype.storm.tuple.Fields;
import backtype.storm.testing.TestGlobalCount;
import backtype.storm.Config;
import backtype.storm.LocalCluster;
import backtype.storm.utils.Utils;

/**
 * This topology demonstrates Storm's stream groupings and multilang
 * capabilities.
 */
public class ExampleTopology {
     public static void main(String args[]){
          TopologyBuilder builder = new TopologyBuilder();
          builder.setSpout("1", new TestWordSpout(true), 5);
          builder.setSpout("2", new TestWordSpout(true), 3);
          builder.setBolt("3", new TestWordCounter(), 3)
                  .fieldsGrouping("1", new Fields("word"))
                  .fieldsGrouping("2", new Fields("word"));
          builder.setBolt("4", new TestGlobalCount())
                  .globalGrouping("1");

          Map conf = new HashMap();
          conf.put(Config.TOPOLOGY_WORKERS, 4);
          try {
//               StormSubmitter.submitTopology("mytopology", conf, builder.createTopology());
               LocalCluster cluster = new LocalCluster("gx.master", 2181L);
//               cluster.submitTopologyWithOpts();
               cluster.submitTopology("mytopology", conf, builder.createTopology());
               Utils.sleep(10000);
               cluster.shutdown();
          }
          catch(Exception e){
               e.printStackTrace();
          }

     }

}
