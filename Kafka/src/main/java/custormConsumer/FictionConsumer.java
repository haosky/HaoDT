package custormConsumer;

import customProduct.FunctionsKafkaProduct;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.ConsumerRecord;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;
import java.util.Arrays;

import crawler.contentextractor.crawmodels.FunctionOP;
import customSerializer.FnctionsDecoder;
/**
 * Created by gxkj-941 on 2017/4/1.
 */
public class FictionConsumer<K,V> {
    private KafkaConsumer<K,V> consumer = null;
    public FictionConsumer(String strServers)
    {
        Properties props = new Properties();
        props.put("bootstrap.servers", strServers);
        props.put("group.id", "test");
//        props.put("client.id", "0");
        props.put("enable.auto.commit", "true");
        props.put("auto.commit.interval.ms", "1000");
        props.put("session.timeout.ms", "30000");
        props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        props.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        this.consumer = new KafkaConsumer<>(props);
    }

    public FictionConsumer(String strServers,Properties props)
    {
        props.put("bootstrap.servers", strServers);
        this.consumer = new KafkaConsumer<>(props);
    }



    public static void main(String args[]) throws IOException{
        Properties propsettings = new Properties();
        InputStream ins = FictionConsumer.class.getResourceAsStream("../kafkaSettings.properties");

        propsettings.load(ins);
        Properties props = new Properties();
        props.put("group.id", "test3");
        props.put("enable.auto.commit", "true");
        props.put("auto.commit.interval.ms", "1000");
        props.put("session.timeout.ms", "30000");
        props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        props.put("value.deserializer", "customSerializer.FnctionsDecoder");

        FictionConsumer<String,FunctionOP> fpf = new FictionConsumer<String,FunctionOP>(propsettings.getProperty("kafka.servers.address"),props);
        fpf.consumer.subscribe(Arrays.asList("TEMP_FUNCTION_QUEUE3"));
        while (true) {
            ConsumerRecords<String,FunctionOP> records = fpf.consumer.poll(10);
            for (ConsumerRecord<String, FunctionOP> record : records)
                System.out.printf("offset = %d, key = %s, value = %s", record.offset(), record.key(), record.value());
        }
    }
}
