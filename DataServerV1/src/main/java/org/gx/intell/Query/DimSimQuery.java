package org.gx.intell.Query;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransportException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gxthrift.simhandler.sim_query;


public class DimSimQuery
{	
	public static Logger LOG = LoggerFactory.getLogger(DimSimQuery.class);
	sim_query.Client client = null; 
	TSocket transport = null;
	
	public DimSimQuery(){
		
		if(this.transport == null || this.client == null ||!transport.isOpen()){
			Properties prop = new Properties();
			InputStream ins = DimSimQuery.class.getClassLoader().getResourceAsStream("tserverSettings.properties");
			try {
				prop.load(ins);
				this.transport  =new TSocket(prop.getProperty("gxthrift.simhandler.host"),
						Integer.parseInt(prop.getProperty("gxthrift.simhandler.port")));
				transport.open();
			} catch (TTransportException e) {
				// TODO Auto-generated catch block
				LOG.error(e.getMessage());
			} catch (IOException e) {
				// TODO Auto-generated catch block
				LOG.error(e.getMessage());
			}
			TProtocol protocol = new TBinaryProtocol(transport);
			this.client = new sim_query.Client(protocol);
	    }
	}
	
	public String simCompanyQuery(String company_name){
		String result = "[]";
		try {
			result = this.client.sim_unit_query(company_name);
		} catch (TException e) {
			// TODO Auto-generated catch block
			LOG.error(e.getMessage());
		}
		destory();
		return result;		
	}
	
	public String simUserQuery(String user_name){
		String result = "[]";
		try {
			result = this.client.sim_user_query(user_name);
		} catch (TException e) {
			// TODO Auto-generated catch block
			LOG.error(e.getMessage());
		}
		destory();
		return result;		
	}
	
	public String simProjectQuery(String project_name){
		String result = "[]";
		try {
			result = this.client.sim_project_query(project_name);
		} catch (TException e) {
			// TODO Auto-generated catch block
			LOG.error(e.getMessage());
		}
		destory();
		return result;		
	}
	
//	public String extractKeyWords(String content){
//		String result = "[]";
//		try {
//			result = this.client.keyword_query(content);
//		} catch (TException e) {
//			// TODO Auto-generated catch block
//			LOG.error(e.getMessage());
//		}
//		destory();
//		return result;	
//	}
	
	//融合搜索详情
	//{"params":{"_uuid":"435f392b908a44442c9125ee2c542af0"},"model":"applications.multisearch.MainServer","action":"get_body_compx_info"}
	//融合搜索列表
	//{"params":{"entry":"要搜索的关键字"},"model":"applications.multisearch.MainServer","action":"search_art_keyword"}
		
	public String commonQuery(String jsonParams){
		String result = null;
		try {
			result = this.client.common_query_api(jsonParams);
		} catch (TException e) {
			// TODO Auto-generated catch block
			LOG.error(e.getMessage());
		}
		destory();
		return result;	
	}
	
	public String queryTopics(String content){
		String result = "[]";
		try {
			result = this.client.topic_query(content);
		} catch (TException e) {
			// TODO Auto-generated catch block
			LOG.error(e.getMessage());
		}
		destory();
		return result;	
	}
	
	
	public String extractEntryWords(String content){
		String result = "[]";
		try {
			result = this.client.entry_word_query(content);
		} catch (TException e) {
			// TODO Auto-generated catch block
			LOG.error(e.getMessage());
		}
		destory();
		return result;	
	}
	
	public String extractNewWords(String content){
		String result = "[]";
		try {
			result = this.client.new_word_query(content);
		} catch (TException e) {
			// TODO Auto-generated catch block
			LOG.error(e.getMessage());
		}
		destory();
		return result;	
	}
	
	public void destory(){
		try{
			this.transport.close();
		}catch(Exception e){
			LOG.error(e.getMessage());
		}
		this.client = null;
	}
	
    public static void main( String[] args )
    {
    	// 项目只能查询
//    	String str = new DimSimQuery().simProjectQuery("地震监视防御区经费");   
    	// 用户只能查询
//		String str = new DimSimQuery().simUserQuery("永红");   	 
    	
    	//公司只能查询
//		String str = new DimSimQuery().simCompanyQuery("广东职业");   	 
    	
    	//融合搜索详情
    	//{"params":{"_uuid":"435f392b908a44442c9125ee2c542af0"},"model":"applications.multisearch.MainServer","action":"get_body_compx_info"}
    	//融合搜索列表
    	//{"params":{"entry":"要搜索的关键字"},"model":"applications.multisearch.MainServer","action":"search_art_keyword"}
//    	String params = "{\"params\":{\"_uuid\":\"00039b29c51204dab845c61a599bab35\"},\"model\":\"applications.multisearch.MainServer\",\"action\":\"search_art_keyword\"}";
    	String params = "{\"params\":{\"entry\":\"发工资\"},\"model\":\"applications.multisearch.MainServer\",\"action\":\"search_art_keyword\"}";
    	String str = new DimSimQuery().commonQuery(params);
    	System.out.println(str);
    }
}


