package dataetlv1;

import java.io.BufferedReader;
import java.io.File;

import cushtml.pdfextraction.GuangDongFinancialPDFStruct;
import cushtml.pdfextraction.GuangDongFinanicalPDF2Html;

import org.apache.hadoop.hbase.client.Put;
import hbaseutils.HbaseDao;
import java.util.HashMap;
import java.util.List;
import java.util.ArrayList;
import org.gx.intell.Query.ContentSimQuery;

import customcommon.FileUtils;
import customcommon.StrUtils;

public class YiAnJYFiles {
	
	public static void main(String args[])
	{	
		HbaseDao hdao = new HbaseDao();
		try{
//			File pdfdir = new File("D:\\建议原文_标题");
//			File[] pdfs = pdfdir.listFiles();
//			for(File dirctory : pdfs){
				try{
//					
//					if(dirctory.isDirectory()){
					File dirctory = new File("D:\\议案原文_标题\\2012");
					for(File file : dirctory.listFiles()){
							
							
							String fileName = file.getName();
							String title = fileName.split("：")[1];
							BufferedReader bff = FileUtils.getFile2BuffRead(file);
							String str = null;
							StringBuffer contbuff = new StringBuffer();
							while((str = bff.readLine()) !=null)
								contbuff.append(str);
							 
							String hd5findename = StrUtils.toMd5Str(fileName);
							
							
							String content = contbuff.toString().replace("\n", "");
							
							String[] phases = content.split("。");
							int pid = 0;
							for(String p :phases){
								if(p == null)
									continue;
								ContentSimQuery cq = new ContentSimQuery();
								System.out.println(p);
								String psim = cq.getConentSimHash(p.trim());
//								System.out.println(psim);
								if(psim == null ){
									break;
								}
								pid +=1;
								String pid_str = psim+":"+hd5findename+":"+pid;
								Put parsePut = new Put(pid_str.getBytes());
								parsePut.addColumn("a".getBytes(), "phase".getBytes(), p.getBytes());
								parsePut.addColumn("a".getBytes(), "phaseId".getBytes(), (pid+"").getBytes());
								parsePut.addColumn("a".getBytes(), "docId".getBytes(), hd5findename.getBytes());
								hdao.put("YAJYPhase", parsePut);
								
							}
							
							
							Put p = new Put(hd5findename.getBytes());
							
							p.addColumn("a".getBytes(), "title".getBytes(), title.getBytes());
							p.addColumn("a".getBytes(), "content".getBytes(), content.getBytes());
							
							hdao.put("YAJY", p);
//						}
					}
		 
				}catch(Exception e){
					e.printStackTrace();
					}
//				}
			
			
			}catch(Exception e){
				e.printStackTrace();
			}finally{
				hdao.destory();
			}
	}

}
