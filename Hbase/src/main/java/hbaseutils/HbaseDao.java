package hbaseutils;

import java.io.IOException;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.lang.reflect.Field;
import java.util.*;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.Cell;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.TableName;
import org.apache.hadoop.hbase.client.Connection;
import org.apache.hadoop.hbase.client.ConnectionFactory;
import org.apache.hadoop.hbase.client.Get;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.ResultScanner;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.client.Table;
import org.apache.hadoop.hbase.util.Bytes;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import hbasesrc.HbaseSettings;
import customcommon.BeanEval;
import hbasemodels.BaseOP;
import customcommon.BeanUtils;
public class HbaseDao{
	public static Logger LOG = LoggerFactory.getLogger(HbaseDao.class);
	private Connection cfn=null;
	public HbaseDao(){
		Properties prop = new Properties();
		InputStream ins = HbaseDao.class.getClassLoader().getResourceAsStream("hbaseSettings.properties");
		try {
			prop.load(ins);
			Configuration conf = HBaseConfiguration.create();
			conf.set("hbase.zookeeper.quorum", prop.getProperty("hbase.zookeeper.host"));
			conf.set("hbase.zookeeper.property.clientPort", prop.getProperty("hbase.zookeeper.port"));
			conf.set("hbase.master", HbaseSettings.HBMASTER);

			 cfn =	ConnectionFactory.createConnection(conf);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			LOG.error(e.getMessage());
		}
	}
	public Result get(String tableName,byte[] rowkey,byte[] family,Iterator<byte[]> columns) throws IOException{
		Table gtable = cfn.getTable(TableName.valueOf(tableName)); 
		Get get = new Get(rowkey);
		while(columns.hasNext()){
			get.addColumn(family, columns.next());
		}
	    Result r = gtable.get(get);
	    try{
	    	gtable.close();
	    }catch(Exception e){
			LOG.error(e.getMessage());
	    }
	    return r;
	}
	public Result get(String tableName,byte[] rowkey,byte[] family,byte[] column) throws IOException{
		Table gtable = cfn.getTable(TableName.valueOf(tableName)); 
		Get get = new Get(rowkey);
	    get.addColumn(family, column);
	    Result r = gtable.get(get);
	    try{
	    	gtable.close();
	    }catch(Exception e){
			LOG.error(e.getMessage());
	    }
	    return r;
	}
	
	public ResultScanner scannRow(String tableName,String familyName,String startKey,String endKey) throws IOException{
		 Scan scan = new Scan(Bytes.toBytes(startKey),Bytes.toBytes(endKey));
		 scan.addFamily(Bytes.toBytes(familyName));
		 Table gtable = cfn.getTable(TableName.valueOf(tableName)); 
		 ResultScanner rs =gtable.getScanner(scan);
		 return rs;
	}
	
	public ResultScanner scannRow(String tableName,String familyName) throws IOException{
		 Scan scan = new Scan();
		 scan.addFamily(Bytes.toBytes(familyName));
		 Table gtable = cfn.getTable(TableName.valueOf(tableName)); 
		 ResultScanner rs =gtable.getScanner(scan);
		 return rs;
	}
	
	public Iterator<byte[]> getColumnsInColumnFamily(Result r, String ColumnFamily)
	{
		  NavigableMap<byte[], byte[]> familyMap = r.getFamilyMap(Bytes.toBytes(ColumnFamily));
	      List<byte[]> Quantifers = new ArrayList<byte[]>();

	      int counter = 0;
	      for(byte[] bQunitifer : familyMap.keySet())
	      {
	    	  Quantifers.add(bQunitifer);

	      }

	      return Quantifers.iterator();
	}

	public void put(String tableName,List<Put> puts) throws IOException{
		Table gtable = cfn.getTable(TableName.valueOf(tableName)); 
		gtable.put(puts);
		gtable.close();
	}
	
	public void put(String tableName,Put put) throws IOException{
		Table gtable = cfn.getTable(TableName.valueOf(tableName)); 
		gtable.put(put);
		gtable.close();
	}
	
	public void destory(){
		try{
			if(cfn!=null){
				cfn.close();
			}
	 }catch(Exception e){
			LOG.error(e.getMessage());
	    }
	}

	public void putByTableObject(List<BaseOP> oplist,String table){
		HbaseDao hd = new HbaseDao();
		BeanEval<BaseOP> be = new BeanEval<BaseOP>();
		ArrayList<Put> listPut = new ArrayList<Put>();
		try {
			for(BaseOP fo :oplist) {
				Field[] fields = be.getEntryFields(fo);
				byte[] rowkey = fo.getRowKey();
				Put put = new Put(rowkey);
				for (Field entryField : fields) {
					Object ob = entryField.get(fo);
					put.addColumn("a".getBytes(), entryField.getName().getBytes(), BeanUtils.ObjectToBytes(ob));
				}
				listPut.add(put);
			}
		}catch (Exception e){e.printStackTrace();}
		try {
			hd.put(table, listPut);
			hd.destory();
		}catch (IOException e){e.printStackTrace();}
	}
	
	public static String getCellData(Result value,String column,String cFamily) throws UnsupportedEncodingException{
		String result = null;
		
		List<Cell> cr =value.getColumnCells(cFamily.getBytes(), column.getBytes());
		for(Cell c :cr){
			String cv = Bytes.toString(c.getValueArray(),c.getValueOffset(),c.getValueLength());
			if(! cv.trim().toLowerCase().equals("null")){
				result = cv;
			}
			break;
		}
		return result == null ? "":result;
	}		

}
