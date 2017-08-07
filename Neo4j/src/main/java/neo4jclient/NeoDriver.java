package neo4jclient;
import org.neo4j.driver.v1.*;
import static org.neo4j.driver.v1.Values.parameters;

import java.io.IOException;
import java.util.Properties;
import java.io.InputStream;
/**
 * Created by hao on 2017/3/21.
 */
public class NeoDriver {
    private Session session;
    private Driver driver;

    public Session getSession(){
        return this.session;
    }
    public void setSession(Session session){
        this.session = session;
    }
    public Session createSession() throws IOException{
        Properties prop = new Properties();
        InputStream ins = NeoDriver.class.getClassLoader().getResourceAsStream("neoSettings.properties");
        prop.load(ins);
        driver = GraphDatabase.driver( prop.getProperty("neo4j.bolt.address"), AuthTokens.basic( prop.getProperty("neo4j.user"), prop.getProperty("neo4j.password") ) );
        session = driver.session();
        return session;
    }

    public void destoryDriver(){
        try{
            session.close();
            if(driver != null)
            driver.close();
        }catch (Exception e){
            e.printStackTrace();
        }
    }

    public void runPutStatement(String cypher,Value var2){
        try {
            this.session.run(cypher,var2);
        }catch (Exception e){
            e.printStackTrace();
        }
    }

    public StatementResult runQueryStatement(String cypher,Value var2) {
        StatementResult result = null;
        try {
            result = session.run(cypher,
                    var2);
        }catch (Exception e){
            e.printStackTrace();
        }
        return result;
    }

    public static void main(String args[]) throws IOException{
        NeoDriver nd = new NeoDriver();
        Session session = nd.createSession();
        
        nd.runPutStatement( "MERGE   (a:Person {name:{name},title:{title}}) ON CREATE SET a.name = {name}",
        parameters( "name", "n51", "title", "King25" ) );
       
        nd.runPutStatement( "MERGE   (b:Person {name:{name},title:{title}}) ON CREATE SET b.name = {name}",
                parameters( "name", "Arthur13x", "title", "add" ) );
    	
        nd.runPutStatement("MATCH (c:Person {name: {name}}) "
				+ "MATCH (d:Person {name: {name1}}) "
				+ "MERGE (c)-[r:LOVE] -> (d) "
				+ "ON CREATE SET  r.name = {name} "
				+ "ON MATCH SET  r.name = {name1} and r.title = {title}",
                  parameters("name","n51","name1","Arthur13x","title","add") );		
        nd.destoryDriver();
    }
}
