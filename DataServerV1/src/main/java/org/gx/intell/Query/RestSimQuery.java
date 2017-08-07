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

import gxthrift.simhandler.rest_develop;


public class RestSimQuery
{	
	public static Logger LOG = LoggerFactory.getLogger(RestSimQuery.class);
	rest_develop.Client client = null; 
	TSocket transport = null;
	
	public RestSimQuery(){
		
		if(this.transport == null || this.client == null ||!transport.isOpen()){
			Properties prop = new Properties();
			InputStream ins = RestSimQuery.class.getClassLoader().getResourceAsStream("tserverSettings.properties");
			try {
				prop.load(ins);
				this.transport  =new TSocket(prop.getProperty("gxthrift.resthandler.host"),
						Integer.parseInt(prop.getProperty("gxthrift.resthandler.port")));
				transport.open();
			} catch (TTransportException e) {
				// TODO Auto-generated catch block
				LOG.error(e.getMessage());
			} catch (IOException e) {
				// TODO Auto-generated catch block
				LOG.error(e.getMessage());
			}
			TProtocol protocol = new TBinaryProtocol(transport);
			this.client = new rest_develop.Client(protocol);
	    }
	}
	
	public String getEntryRelative(String uuid,int num){
		String result = null;
		try {
			result = this.client.get_entry_relative(uuid, num);
		} catch (TException e) {
			// TODO Auto-generated catch block
			LOG.error(e.getMessage());
		}
		destory();
		return result;		
	}
	
	public String getRelativeList(String search_str){
		String result = null;
		try {
			result = this.client.get_relative_list(search_str);
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
//		String str = new RestSimQuery().getEntryRelative("47985d37bf3b4e82b97ce6eeaec437bc",10);   	 
//    	System.out.println(str);
    	//查询列表
    	String str = new RestSimQuery().getRelativeList("申报书");   	 
    	System.out.println(str);
    }
}


