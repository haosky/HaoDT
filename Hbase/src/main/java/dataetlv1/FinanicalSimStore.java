package dataetlv1;

import java.io.File;

import cushtml.pdfextraction.GuangDongFinancialPDFStruct;
import cushtml.pdfextraction.GuangDongFinanicalPDF2Html;

import org.apache.hadoop.hbase.client.Put;
import hbaseutils.HbaseDao;
import java.util.HashMap;
import java.util.List;
import java.util.ArrayList;
import org.gx.intell.Query.ContentSimQuery;

import customcommon.StrUtils;

public class FinanicalSimStore {
	
	public static void main(String args[])
	{	
		HbaseDao hdao = new HbaseDao();
		try{
			File pdfdir = new File("D:\\workspace\\budgetNum");
			File[] pdfs = pdfdir.listFiles();
			List<Put> puts = new ArrayList<Put>();
			
			for(File f : pdfs){
				try{
				GuangDongFinanicalPDF2Html g = new GuangDongFinanicalPDF2Html(f.getPath());
				GuangDongFinancialPDFStruct gstruct = g.getExtraction();
				if(gstruct.getOrganization( ) != null){
					//int code = es.upsetData("guangdongfinanical", "Pdfs", gstruct.getMapKeyValue(),gstruct.getFilename());
					ContentSimQuery cq = new ContentSimQuery();
					HashMap<String, Object> hm = gstruct.getMapKeyValue();
					String content = hm.get("content").toString();
					String filename = hm.get("filename").toString();
					String title = hm.get("title").toString();
					String id = cq.getConentSimHash(content);
					System.out.println(id);
					String hd5findename = StrUtils.toMd5Str(filename);
					Put p = new Put((id+hd5findename).getBytes());
				 
					p.addColumn("a".getBytes(), "filename".getBytes(), filename.getBytes());
					p.addColumn("a".getBytes(), "content".getBytes(), content.getBytes());
					p.addColumn("a".getBytes(), "title".getBytes(), title.getBytes());
					p.addColumn("a".getBytes(), "simhash".getBytes(), id.getBytes());
					p.addColumn("a".getBytes(), "hd5findename".getBytes(), hd5findename.getBytes());
					
					puts.add(p);
					System.out.println((id+hd5findename));
				}
				}catch(Exception e){
					e.printStackTrace();
					}
				}
			hdao.put("GDFinancialPDFSim", puts);
			}catch(Exception e){
				e.printStackTrace();
			}finally{
				hdao.destory();
			}
	}

}
