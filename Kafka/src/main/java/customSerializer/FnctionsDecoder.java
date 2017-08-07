package customSerializer;
import java.util.Map;
import org.apache.kafka.common.errors.SerializationException;
import org.apache.kafka.common.serialization.Deserializer;
import customcommon.BeanUtils;
import crawler.contentextractor.crawmodels.FunctionOP;

public class FnctionsDecoder implements Deserializer<FunctionOP> {

    public FnctionsDecoder() {

    }

    public void configure(Map<String, ?> configs, boolean isKey) {

    }

    public FunctionOP deserialize(String topic, byte[] data) {
        try {
            if(data == null)
                return null;
            return (FunctionOP)BeanUtils.BytesToObject(data);
        } catch (Exception var4) {
            throw new SerializationException("Error when deserializing byte[] to  " );
        }
    }

    public void close() {
    }
}
