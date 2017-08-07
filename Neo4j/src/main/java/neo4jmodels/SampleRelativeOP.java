package neo4jmodels;

import org.neo4j.driver.v1.Value;

import static org.neo4j.driver.v1.Values.parameters;

/**
 * Created by gxkj-941 on 2017/4/6.
 */
public class SampleRelativeOP extends BaseEntryOP{
    private String relativeLabel=null;
    private String relativeRank=null;
    private String relativeRankName=null;
    private String entryLabel=null;
    private String entrySlave=null;
    private String entryMaster=null;
    private String entryKey=null;

    public String makeCypher(){
        return "MATCH (a:"+this.entryLabel+" {"+entryKey+": {"+entryKey+"1}}),\\n\" +\n" +
"                                 \"      (b:"+this.entryLabel+" {"+entryKey+": {"+entryKey+"2}})\\n\" +\n" +
"                                 \"MERGE (a)-[r:"+this.relativeLabel+"]->(b)\\n\" +\n" +
"                                 \"  ON CREATE SET  r."+relativeRankName+" = {"+relativeRankName+"}\\n\" +\n" +
"                                 \"  ON MATCH SET  r."+relativeRankName+" = {"+relativeRankName+"}";
    }
    public Value markParams(){
        return parameters(entryKey+"1",this.entryMaster,entryKey+"2",entrySlave,relativeRankName,relativeRank);
    }
}
