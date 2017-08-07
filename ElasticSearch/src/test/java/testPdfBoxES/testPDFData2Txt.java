package testPdfBoxES;

import java.io.File;
import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.net.UnknownHostException;

import org.junit.Test;

import cushtml.pdfextraction.GuangDongFinancialPDFStruct;
import cushtml.pdfextraction.GuangDongFinanicalPDF2Html;

public class testPDFData2Txt {
	
	@Test
	public void testIndex() throws UnknownHostException{

		System.out.println("----");
		try{
			File pdfdir = new File("D:\\workspace\\budgetNum");
			File[] pdfs = pdfdir.listFiles();
			for(File f : pdfs){
				try{
				GuangDongFinanicalPDF2Html g = new GuangDongFinanicalPDF2Html(f.getPath());
				GuangDongFinancialPDFStruct gstruct = g.getExtraction();
				if(gstruct.getOrganization( ) != null){
					File outfile = new File("D:\\workspace\\pdf2txt\\"+f.getName()+".txt");
					FileOutputStream os = new FileOutputStream(outfile);
					BufferedOutputStream bout = new BufferedOutputStream(os);
					bout.write(gstruct.getContent().getBytes());
					bout.close();
				}
				}catch(Exception e){
					e.printStackTrace();
					}
				}
			
			}catch(Exception e){
				e.printStackTrace();
			}finally{
				
			}
		}
}
