package mongotablesv1;
import customcommon.MongoDBUtils;
import hbaseutils.HbaseDao;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.hadoop.hbase.client.Put;
import org.bson.Document;
import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;

import com.mongodb.MongoClient;
import com.mongodb.MongoCredential;
import com.mongodb.ServerAddress;
import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;

public class L1_PROJECT_M2H {
	public static Log log = LogFactory.getLog(L1_PROJECT_M2H.class);
	
public static void main(String args[]){
		
		MongoDBUtils mdbutils = new MongoDBUtils();
		try{

			MongoCredential credential = MongoCredential.createCredential("admin", "DStore", "tingting".toCharArray()); 
			ServerAddress serverAddress = new ServerAddress("192.168.1.12", 27020); 
			MongoClient mcu = new MongoClient(serverAddress, Arrays.asList(credential)); 
	         // 连接到数据库
	         MongoDatabase mongoDatabase = mcu.getDatabase("DStore");  
	         System.out.println("Connect to database successfully");
	         MongoCollection<Document> collection = mongoDatabase.getCollection("ALLTABLE");
			 
			 FindIterable<Document> findIterable = collection.find().noCursorTimeout(true); 
	         MongoCursor<Document> mongoCursor = findIterable.iterator();  
	        
	         int i =0 ;
	         int count = 1000;
	         List<Put> listPut = new ArrayList<Put>();
	         
	         HbaseDao hdao =  new HbaseDao();
	         while(mongoCursor.hasNext()){  
	        	 Document D = mongoCursor.next();  
	        	 if(i >= count){
	        		  hdao.put("ALLTABLES", listPut);
//	        		  hdao.destory();
//	        		  hdao = new HbaseDao();
	        		  listPut =  new ArrayList<Put>();
	        		  i = 0;
	        		  log.info("---put--");
	        	 }
	        	
	        	 String rowkey = D.getString("_ROWKEY");
	        	 System.out.println(rowkey);
	        	 Put p = new Put(rowkey.getBytes());
	        	 
	        	 ArrayList<String> KEYWORDS = (ArrayList<String>)D.get("KEYWORDS");
	        	 String COLUMN_NAME = D.getString("COLUMN_NAME");
	        	 String COLUMN_VALUE = D.get("COLUMN_VALUE").toString();
	        	 String COLUMN_COMMENTS = D.getString("COLUMN_COMMENTS");
	        	 
	        			 	
				 p.addColumn("a".getBytes(), "COLUMN_NAME".getBytes(), COLUMN_VALUE.getBytes());
				 p.addColumn("a".getBytes(), (COLUMN_NAME+"__STR").getBytes(), COLUMN_NAME.getBytes());
				 p.addColumn("a".getBytes(), (COLUMN_NAME+"__COMMENTS").getBytes(), COLUMN_COMMENTS.getBytes());
				 p.addColumn("a".getBytes(), (COLUMN_NAME+"__KEYWORDS").getBytes(), KEYWORDS.toString().getBytes());
	        	 
	        	 listPut.add(p);
	        	 i +=1;
	         }  
			 
	         hdao.put("ALLTABLES", listPut);
   		  	 hdao.destory();
		  
		}catch(Exception e){
			e.printStackTrace();
		}
		finally{
			mdbutils.destory();
		}
	}

	private static void find() {
		// TODO Auto-generated method stub
		
	}

}
