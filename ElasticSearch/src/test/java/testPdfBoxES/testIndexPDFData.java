package testPdfBoxES;

import java.io.File;
import java.net.UnknownHostException;

import org.junit.Test;

import cushtml.pdfextraction.GuangDongFinancialPDFStruct;
import cushtml.pdfextraction.GuangDongFinanicalPDF2Html;
import esclient.elsaticsearchUtils;

public class testIndexPDFData {
	
	@Test
	public void testIndex() throws UnknownHostException{
		elsaticsearchUtils es = new elsaticsearchUtils("192.168.18.236:9300");
		System.out.println("----");
		try{
			File pdfdir = new File("D:\\workspace\\budgetNum");
			File[] pdfs = pdfdir.listFiles();
			for(File f : pdfs){
				try{
				GuangDongFinanicalPDF2Html g = new GuangDongFinanicalPDF2Html(f.getPath());
				GuangDongFinancialPDFStruct gstruct = g.getExtraction();
				if(gstruct.getOrganization( ) != null){
					int code = es.upsetData("guangdongfinanical", "Pdfs", gstruct.getMapKeyValue(),gstruct.getFilename());
					System.out.println(code);
				}
				}catch(Exception e){
					e.printStackTrace();
					}
				}
			
			}catch(Exception e){
				e.printStackTrace();
			}finally{
				es.destory();
			}
		}
}
