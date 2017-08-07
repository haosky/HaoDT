package pdfboxtests;

import org.junit.Test;

import java.io.File;

import cushtml.pdfextraction.GuangDongFinancialPDFStruct;
import cushtml.pdfextraction.GuangDongFinanicalPDF2Html;
import customcommon.MongoDBUtils;

public class TestPdfbox {
	
	@Test
	public void testPutData(){
	MongoDBUtils mdb = new MongoDBUtils();
	try{
		mdb.createClient("mongodb://admin:tingting@192.168.1.12:27020/admin?connectTimeoutMS=30000000&maxIdleTimeMS=60000000");
		File pdfdir = new File("D:\\workspace\\budgetNum");
		File[] pdfs = pdfdir.listFiles();
		for(File f : pdfs){
			try{
			GuangDongFinanicalPDF2Html g = new GuangDongFinanicalPDF2Html(f.getPath());
			GuangDongFinancialPDFStruct gstruct = g.getExtraction();
			if(gstruct.getOrganization( ) != null)
				mdb.insertOrUpdateForMap(gstruct.getMapKeyValue(), "filename", "DStore", "GuangDongFinanicalPDF"); 
			}catch(Exception e){
				
				}
			}
		
		}catch(Exception e){
			e.printStackTrace();
		}finally{
			mdb.destory();
		}
	}
	
	
}
