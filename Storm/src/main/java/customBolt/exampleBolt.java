package customBolt;

import backtype.storm.task.TopologyContext;
import backtype.storm.topology.BasicOutputCollector;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.base.BaseBasicBolt;
import backtype.storm.tuple.Fields;
import backtype.storm.tuple.Tuple;
import backtype.storm.utils.Utils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.Map;

/**
 * Created by gxkj-941 on 2017/4/5.
 */
public class exampleBolt extends BaseBasicBolt {
    public static Logger LOG = LoggerFactory.getLogger(exampleBolt.class);
    Map<String, Integer> _counts;

    public exampleBolt() {
    }

    public void prepare(Map stormConf, TopologyContext context) {
        LOG.info("new starts。。。。。。。。。");
        this._counts = new HashMap();
    }

    public void execute(Tuple input, BasicOutputCollector collector) {
        String word = (String)input.getValues().get(0);
        LOG.info("---------------------aaaaabbbbbbbbbb:=-"+word);
        int count = 0;
        if(this._counts.containsKey(word)) {
            count = this._counts.get(word).intValue();
        }

        ++count;
        this._counts.put(word, Integer.valueOf(count));
        LOG.info("---------------------aaaaabbbbbbbbbb:=-"+count);
        collector.emit(Utils.tuple(word, Integer.valueOf(count)));
    }

    public void cleanup() {
        LOG.info("cleanup。。。。");
    }
    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        declarer.declare(new Fields("word", "count"));
    }
}
