package neo4jmodels;

import org.neo4j.driver.v1.Value;
import static org.neo4j.driver.v1.Values.parameters;
/**
 * Created by gxkj-941 on 2017/4/6.
 */
public class SampleEntryOP extends BaseEntryOP{
    private String label=null;
    private String name=null;
    private String sex=null;

    public String makeCypher(){
        return "MERGE (a:"+this.label+" {name:{name},sex:{sex}})";
    }
    public Value markParams(){
        return parameters("name",this.name,"sex",this.sex);
    }
}
