package customProduct;
import crawler.contentextractor.crawmodels.FunctionOP;
import cushtml.analyEbookHtm;
import customSerializer.FunctionsEncoder;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;
import java.io.File;

/**
 * Created by gxkj-941 on 2017/4/5.
 */
public class FunctionsKafkaProduct {
    public static final String QUEUE = "TEMP_FUNCTION_QUEUE3";

    public static void main(String args[]){
        Properties propsettings = new Properties();
        InputStream ins = FunctionsKafkaProduct.class.getResourceAsStream("../kafkaSettings.properties");
        try {
            propsettings.load(ins);
            Properties props = new Properties();
            props.put("acks", "all");
            props.put("retries", 0);
            props.put("batch.size", 1384);
            props.put("linger.ms", 1);
            props.put("buffer.memory", 44432);
            props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
            props.put("value.serializer", FunctionsEncoder.class.getName());
            FictionProcFactory<String,FunctionOP> fpf = new FictionProcFactory<String,FunctionOP>(propsettings.getProperty("kafka.servers.address"),QUEUE,props);
            File fileDirs = new File("D:\\ddd");
            File[] listFunctions = fileDirs.listFiles();
            for(File f : listFunctions){
                System.out.println(f.getPath());
                analyEbookHtm aehM = new analyEbookHtm();
                analyEbookHtm aeh = aehM.anayToContent(f);

                String title = aeh.parsTitle();
                String content = aeh.parsContent();
                String subTitle = f.getName().replace(".htm","");
                System.out.println(subTitle);
                System.out.println(content);
                FunctionOP fo = new FunctionOP();

                fo.setContent(content);
                fo.setSubTitle(title);
                fo.setSubTitle(subTitle);

                fpf.buildQueue(fo);
                System.out.println("build success");
                break;
            }
        fpf.flushProdut();
        fpf.closeProduct();

    }catch(IOException e)
            {e.printStackTrace();
        }
    }
}
