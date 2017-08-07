package customcommon;


import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.bson.Document;

import com.mongodb.ConnectionString;
import com.mongodb.ServerAddress;
import com.mongodb.async.SingleResultCallback;
import com.mongodb.async.client.MongoClient;
import com.mongodb.async.client.MongoClientSettings;
import com.mongodb.async.client.MongoClients;
import com.mongodb.async.client.MongoCollection;
import com.mongodb.async.client.MongoDatabase;
import com.mongodb.connection.ClusterSettings;

/**
 * Created by gxkj-941 on 2017/3/31.
 */
public class MongoDBUtils {
	public static Log log = LogFactory.getLog(MongoDBUtils.class);
	private MongoClient client=null;
	
	public MongoClient createClient(String connstr){
		if(client == null){
		 client =  MongoClients.create(new ConnectionString(connstr));
		 log.info("connection from " +connstr);
		}
		return client;
	}
	
	public MongoClient getClient(){
		return this.client;
	}
	
	public MongoCollection<Document> getCollection(String database,String collection){
		MongoDatabase mdatabase = this.client.getDatabase(database);
		MongoCollection<Document> mcollection = mdatabase.getCollection(collection);
		return mcollection;
	}
	
	public void search(){
		
	}
	
	public void insertOrUpdateForMap(Map<String,Object> datas,String primateKey,String database,String collection){
		Document document = new Document(datas);
//		UpdateOptions option = new UpdateOptions() ;
//		option.upsert(true);
//
		MongoCollection<Document> collco = this.getCollection(database, collection);
//		collco.updateMany(Filters.eq(primateKey,datas.get(primateKey)), document,option, new SingleResultCallback<UpdateResult>() {
//
//			@Override
//			public void onResult(UpdateResult result, Throwable arg1) {
//				// TODO Auto-generated method stub				 
//				//System.out.println(result.getModifiedCount());
//			}
//           
//        });
		collco.insertOne(document, new SingleResultCallback<Void>(){

			@Override
			public void onResult(Void arg0, Throwable arg1) {
				// TODO Auto-generated method stub
				
			}
		});
	}
	
	public void destory(){
		client.close();
	}
	
}
