package neo4jmodels;

import org.neo4j.driver.v1.Value;
import java.io.Serializable;

/**
 * Created by gxkj-941 on 2017/4/6.
 */
public abstract class BaseEntryOP implements Serializable {
    public abstract String makeCypher();
    public abstract Value markParams();

}
