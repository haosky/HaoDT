package customProduct;

import org.apache.kafka.clients.producer.KafkaProducer;
import java.util.Properties;
import org.apache.kafka.clients.producer.ProducerRecord;

/**
 * Created by gxkj-941 on 2017/4/1.
 */
public class FictionProcFactory<K,V> {
    private KafkaProducer<K,V> producer = null;
    private String topics = null;
    public FictionProcFactory(String strServers,String topics)
    {
        Properties props = new Properties();
        props.put("bootstrap.servers", strServers);
        props.put("acks", "all");
        props.put("retries", 0);
        props.put("batch.size", 1384);
        props.put("linger.ms", 1);
        props.put("buffer.memory", 4432);
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
//        props.put("client.id", "0");
        this.producer = new KafkaProducer<>(props);
        this.topics  = topics;
    }

    public FictionProcFactory(String strServers, String topics,Properties props) {
        props.put("bootstrap.servers", strServers);
        this.producer = new KafkaProducer(props);
        this.topics = topics;
    }

    public void buildQueue(K k ,V v){
            producer.send(new ProducerRecord<K, V>(this.topics,k ,v));
    }

    public void buildQueue(V v){
        producer.send(new ProducerRecord<K,V>(this.topics,v));
    }
    public void flushProdut(){this.producer.flush();}
    public void closeProduct(){
        this.producer.close();
    }

    public static void main(String args[]){

        FictionProcFactory<String,String> fpf = new FictionProcFactory<String,String>("gx.master:9092","examples_queue");
        fpf.buildQueue("t1","t2");
        fpf.buildQueue("t3","t4");
        fpf.closeProduct();
    }
}
