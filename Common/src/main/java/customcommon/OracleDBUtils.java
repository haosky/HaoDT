package customcommon;

import org.apache.commons.dbcp2.DataSourceConnectionFactory;
import org.apache.commons.dbutils.QueryRunner;
import org.apache.commons.dbutils.ResultSetHandler;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

import org.apache.commons.dbcp2.BasicDataSource;
import org.apache.commons.dbcp2.BasicDataSourceFactory;
/**
 * Created by gxkj-941 on 2017/3/31.
 */
public class OracleDBUtils {
	public static Log log = LogFactory.getLog(OracleDBUtils.class);
    
	private Connection conn = null;
	
	private BasicDataSource datasource =null;
	
	public OracleDBUtils(String username, String passwd,String address,String database) throws Exception{
		//@[HOST_NAME]:1521/[DATABASE_NAME]
		if(conn == null){
			Properties settings = new Properties();
			settings.setProperty("password", passwd);
			settings.setProperty("url",  "jdbc:oracle:thin:@" + address + ":" + database);
			settings.setProperty("username", username);
			settings.setProperty("driverClassName", "oracle.jdbc.driver.OracleDriver");
			datasource = BasicDataSourceFactory.createDataSource(settings);
			DataSourceConnectionFactory df = new DataSourceConnectionFactory(datasource) ;
			this.conn = df.createConnection();
		}
	}
	
	public Connection getConnection(){
		return this.conn;
	}
	
	
	public List<Object> query(String sqlwithprex,ResultSetHandler<List<Object>> rs,Object[] params) throws SQLException{
		QueryRunner run = new QueryRunner(datasource);
		try{
	
			List<Object> result = run.query(sqlwithprex, rs, params);
		     return result;
		} finally {
 
		}
		
	}
	
	  
	public Object querySingle(String sqlwithprex, ResultSetHandler<Object> rs,Object[] params) throws SQLException{
		QueryRunner run = new QueryRunner(datasource);
		try{
	
			Object result = run.query(sqlwithprex, rs,params);
		     return result;
		} finally {
		}
		
	}
	
	public void destory() throws SQLException{
		this.conn.close();
	}
	
	public static void main(String args[]) throws Exception{
		String user = "sys as sysdba";//把用户名改成这个即可
		String pwd="123456";
		String address="localhost:1521";
		String database = "orcl";
		OracleDBUtils db = new OracleDBUtils(user,pwd,address,database);
		
		ResultSetHandler<List<Object>> rs = new ResultSetHandler<List<Object>>(){

			@Override
			public List<Object> handle(ResultSet rs) throws SQLException {
				List<Object> al = new ArrayList<Object>();
				while(rs.next()){
					al.add(rs.getString(1));
					System.out.println(rs.getString(2));
				}
				return al;
			}
			
		};
		String [] params = new String[]{};
		List<Object> d = db.query("select * from ODSDB.PAY_GL_REL", rs,params);
		db.destory();
		
	}
	
	
	
}
