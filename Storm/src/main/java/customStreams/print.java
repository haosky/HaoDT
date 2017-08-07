package customStreams;

import backtype.storm.tuple.Values;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import storm.trident.operation.BaseFunction;
import storm.trident.operation.TridentCollector;
import storm.trident.tuple.TridentTuple;

/**
 * Created by gxkj-941 on 2017/4/5.
 */
public class print extends BaseFunction {
    public static Logger LOG = LoggerFactory.getLogger(print.class);
    public void execute(TridentTuple tuple, TridentCollector collector) {
        String sentence = tuple.getString(0);
        LOG.info("!!!!!!!!!!!!!!!!!!!"+sentence);
//        System.out.println("!!!!!!!!!!!!!!!!!!!>"+sentence);
//        for(String word: sentence.split(" ")) {
//            collector.emit(new Values(word));
//        }
        for(int i=0;i<=10;i++)
            collector.emit(new Values("aaaaaaaaaaa"));

    }
}