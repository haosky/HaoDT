package customSerializer;

import org.apache.kafka.common.errors.SerializationException;
import org.apache.kafka.common.serialization.Serializer;
import crawler.contentextractor.crawmodels.FunctionOP;
import customcommon.BeanUtils;

import java.util.Map;

/**
 * Created by gxkj-941 on 2017/4/5.
 */
public class FunctionsEncoder implements Serializer<FunctionOP> {
    public FunctionsEncoder(){

    }
    public void configure(Map<String, ?> var1, boolean var2) {

    }

    public byte[] serialize(String var1, FunctionOP var2) {

            return var2 == null ? null : BeanUtils.ObjectToBytes(var2);

    }

    public void close() {

    }

}
