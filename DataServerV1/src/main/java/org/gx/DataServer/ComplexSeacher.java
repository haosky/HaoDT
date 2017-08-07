package org.gx.DataServer;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransportException;
import gxthrift.eshandler.data_complex_query;;


public class ComplexSeacher
{	
	data_complex_query.Client client = null; 
	TSocket transport = null;
	public ComplexSeacher(){
		
		if(this.transport == null || this.client == null ||!transport.isOpen()){
			Properties prop = new Properties();
			InputStream ins = ComplexSeacher.class.getClassLoader().getResourceAsStream("tserverSettings.properties");
			try {
				prop.load(ins);
				this.transport  =new TSocket(prop.getProperty("gxthrift.eshandler.host"),
					Integer.parseInt(prop.getProperty("gxthrift.eshandler.port")));
//				this.transport  =new TSocket("192.168.18.236",
//						9993);
				transport.open();
			} catch (TTransportException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			TProtocol protocol = new TBinaryProtocol(transport);
			this.client = new data_complex_query.Client(protocol);
	    }
	}
	
	public String SearchForContent(String inputStr){
		String result = "[]";
		try {
			result = this.client.search_art_keyword(inputStr);
		} catch (TException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		destory();
		return result;		
	}
	
	public void destory(){
		this.transport.close();
		this.client = null;
	}
	
    public static void main( String[] args )
    {
    	String str = new ComplexSeacher().SearchForContent("广东省人大");   	 
    	System.out.println(str);
    }
}


