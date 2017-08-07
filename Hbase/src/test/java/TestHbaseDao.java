/**
 * Created by gxkj-941 on 2017/3/30.
 */
import com.google.common.io.ByteArrayDataInput;
import com.google.common.primitives.Bytes;
import com.hankcs.hanlp.utility.ByteUtil;

import cushtml.analyEbookHtm;
import cushtml.pdfextraction.GuangDongFinancialPDFStruct;
import cushtml.pdfextraction.GuangDongFinanicalPDF2Html;
import hbasemodels.BaseOP;
import org.junit.Test;
import hbaseutils.HbaseDao;
import hbasemodels.FunctionOP;
import hbasemodels.GuangDongFinancialPDFOP;
import customcommon.BeanEval;
import customcommon.StrUtils;
import java.io.IOException;
import java.lang.reflect.Field;
import java.io.File;
import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.lang.reflect.Type;

import org.apache.hadoop.hbase.Cell;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.ResultScanner;
import org.apache.hadoop.hdfs.util.ByteArray;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.io.ByteArrayOutputStream;
import java.io.ObjectOutputStream;
import java.io.ByteArrayInputStream;
import java.io.ObjectInputStream;
import customcommon.BeanUtils;
import customcommon.MongoDBUtils;
public class TestHbaseDao {
    private static java.lang.Object ByteToObject(byte[] bytes) {
        java.lang.Object obj=new java.lang.Object();
        try {
            // bytearray to object
            ByteArrayInputStream bi = new ByteArrayInputStream(bytes);
            ObjectInputStream oi = new ObjectInputStream(bi);
            obj = oi.readObject();
            bi.close();
            oi.close();
        } catch (Exception e) {
            System.out.println("translation" + e.getMessage());
            e.printStackTrace();
        }
        return obj;
    }

    public static byte[] toByteArray (Object obj) {
        byte[] bytes = null;
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        try {
            ObjectOutputStream oos = new ObjectOutputStream(bos);
            oos.writeObject(obj);
            oos.flush();
            bytes = bos.toByteArray ();
            oos.close();
            bos.close();
        } catch (IOException ex) {
            ex.printStackTrace();
        }
        return bytes;
    }
    
//    @Test
    public void test_hbase() throws  NoSuchMethodException,IllegalAccessException,InvocationTargetException,SecurityException{
        HbaseDao hd = new HbaseDao();
        String paths = "D:\\tmp\\zz\\";
        File fileDirs = new File(paths);
        File[] listFunctions = fileDirs.listFiles();
        BeanEval<FunctionOP> be = new BeanEval<FunctionOP>();
        ArrayList<BaseOP> listPut = new ArrayList<BaseOP>();
        int i =0;
        for(File f : listFunctions){
            try {
            	i+=1;
                System.out.println(f.getPath());
                if(1>=10)break;
                analyEbookHtm aehM = new analyEbookHtm();
                analyEbookHtm aeh = aehM.anayToContent(f);
                String content = aeh.parsContent();
                String subTitle = f.getName().replace(".htm", "").replace(paths, "");
                String title = subTitle.split("_")[0];
                FunctionOP fo = new FunctionOP();
                fo.setContent(content);
                fo.setTitle(title);
                fo.setSubTitle(subTitle);
                listPut.add(fo);
            }catch (Exception e){e.printStackTrace();}
        }
        try {
            hd.putByTableObject(listPut,"functions");
            hd.destory();
        }catch (Exception e){e.printStackTrace();}
    }
    
//    @Test
	public void testPutGuangDongFinanical(){
    	HbaseDao hd = new HbaseDao();
    	ArrayList<BaseOP> listPut = new ArrayList<BaseOP>();
	try{
		File pdfdir = new File("D:\\workspace\\budgetNum");
		File[] pdfs = pdfdir.listFiles();
		for(File f : pdfs){
			try{
			GuangDongFinanicalPDF2Html g = new GuangDongFinanicalPDF2Html(f.getPath());
			GuangDongFinancialPDFStruct gstruct = g.getExtraction();
			if(gstruct.getOrganization( ) != null){
				GuangDongFinancialPDFOP gop = new GuangDongFinancialPDFOP();
				gop.setTitle(gstruct.getTitle());
				gop.setContent(gstruct.getContent());
				gop.setDatetimestr(gstruct.getDatetimestr());
				gop.setFilename(gstruct.getFilename());
				gop.setHtml(gstruct.getHtml());
				gop.setOrganization(gstruct.getOrganization());
				gop.setLetterto(gstruct.getLetterto()); 
				gop.setDocs(gstruct.getDocs());
				
				listPut.add(gop);
			
				}
				}catch(Exception e){
					
					}
				}
		
			}catch(Exception e){
				e.printStackTrace();
			}finally{
				hd.putByTableObject(listPut,"GuangDongFinancialPDF");
	            hd.destory();
			}
	}
    
    @Test
	public void testScan() {
		HbaseDao hd = new HbaseDao();
		try {
			ResultScanner rs = hd.scannRow("CaiZhengMoNiSim", "a");
			Iterator<Result> rlist = rs.iterator();
			int i=0;
			while(rlist.hasNext()){ 
				i+=1;
				if(i>=200)
					break;
				Result r = rlist.next();
				System.out.println(HbaseDao.getCellData(r, "bbdw", "a"));
			}
			
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
    
    
    @Test
	public void testSapmle() {
		HbaseDao hd = new HbaseDao();
		try {
			ResultScanner rs = hd.scannRow("ALLTABLES", "a");
			Iterator<Result> rlist = rs.iterator();
			int i=0;
			while(rlist.hasNext()){ 
				i+=1;
				if(i>=200)
					break;
				Result value = rlist.next();
				String data_row_key = new String(value.getRow(),"utf-8");
				String[] cols = data_row_key.split("::")[0].split(":");	
			 	int esid = StrUtils.toUUID(data_row_key);
				StringBuilder sb = new StringBuilder();
				ArrayList<String> keywords = new ArrayList<String>();
				StringBuilder kb = new StringBuilder();
			 	String iCFAMILY = "a";
			 	System.out.println(data_row_key);
			 	for(String s:cols){
					System.out.println(s+"----------------");
					String v = "";
					List<Cell> cr =value.getColumnCells(iCFAMILY.getBytes(), s.getBytes());
					for(Cell c :cr){
						v = new String(c.getValueArray(),c.getValueOffset(),c.getValueLength());
						break;
					}
					
					//列对应中文名称
					String cloumn_name = "";
					
					List<Cell> crc =value.getColumnCells(iCFAMILY.getBytes(), (s+"__STR").getBytes());
					for(Cell c :crc){
						cloumn_name = new String(c.getValueArray(),c.getValueOffset(),c.getValueLength());
						break;
					}
					
					//列对应中文描述
					String cloumn_comments = "";

					List<Cell> crs = value.getColumnCells(iCFAMILY.getBytes(), (s+"__COMMENTS").getBytes());
					for(Cell c :crs){
						cloumn_comments = new String(c.getValueArray(),c.getValueOffset(),c.getValueLength());
						break;
					}
					
					//列对应的所包含的关键字
					String cloumn_keywords =  "[]";
					
					List<Cell> crk = value.getColumnCells(iCFAMILY.getBytes(), (s+"__KEYWORDS").getBytes());
					for(Cell c :crk){
						cloumn_keywords = new String(c.getValueArray(),c.getValueOffset(),c.getValueLength());
						break;
					}
					
					
					if(cloumn_keywords.length() > 8 && cloumn_keywords.contains(",")){
//						cloumn_keywords = cloumn_keywords
						cloumn_keywords = cloumn_keywords.replace("[", "").replace("]", "");
						for(String str : cloumn_keywords.split(",")){
							str = str.trim();
							String strin = "\""+str.trim()+"\"";
							if(keywords.contains(strin))
								continue;
							keywords.add(strin);
							kb.append(str+",");
						}
					}

					sb.append("\""+s+"\":\""+v+"\",");
					sb.append("\""+s+"__STR\":\""+cloumn_name+"\",");
					sb.append("\""+s+"__COMMENTS\":\""+cloumn_comments+"\",");

				}
				sb.append("\"keywords_str\":\""+kb.toString().replace("\"", "").replace("\'", "")+"\",");
				String source = "{\"_id\":\""+esid+"\","+sb.toString()+"\"KEYWORDOBJ\":"+keywords.toString()+"}";
			 	System.out.println(source);
			}
			
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
}
