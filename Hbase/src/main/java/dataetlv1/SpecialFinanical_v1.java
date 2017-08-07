package dataetlv1;

import java.io.File;
import java.io.FileFilter;

import cushtml.pdfextraction.GuangDongSpecFinanicalPDF2Html_V1;
import cushtml.pdfextraction.GuangDongSpecFinanicalPDF2Struct_V1;
import textextraction.word.Word2Text;

import org.apache.hadoop.hbase.client.Put;
import hbaseutils.HbaseDao;
import java.util.HashMap;
import java.util.List;
import java.util.ArrayList;
import customcommon.StrUtils;

public class SpecialFinanical_v1 {
	
	
	
	private static String[] splitFileName(String fileName){
		if(fileName.contains("_") )
			return fileName.split("_");
		String startPrex = "0123456789abcdefghijzlnmopqrstuvwxyz-()";
		char[] carset = fileName.toLowerCase().toCharArray();
		int i = 0;
		for(char c : carset){
			if(! startPrex.contains(c+""))
				break;
			i+=1;
		}
		try{
		String[] result = {fileName.substring(0,i-1),fileName.substring(i)};
		return result;
		}catch(Exception e){
			e.printStackTrace();
		}
		return null;
	}
	
	/*提取word文件*/
	public static void wordextract(){
		HbaseDao hdao = new HbaseDao();
		try{
			File worddir = new File("E:\\专项资金\\uploads");
			File[] words = worddir.listFiles(new FileFilter(){

				@Override
				public boolean accept(File pathname) {
					// TODO Auto-generated method stub
					try{
					if(pathname.getName().endsWith(".docx") || pathname.getName().endsWith(".doc") )
						return true;
					}catch(Exception e){
						e.printStackTrace();
					}
					return false;
				}
				
			});
			List<Put> puts = new ArrayList<Put>();
			int maxsize = 100;
			int i = maxsize;
			int all = words.length;
			int current = 0 ;
			System.out.println(all);
			for(File f : words){
				try{
//					System.out.println(f.getName());
					i-=1;
					current+=1;
					if(current <=7700 || current == 7829)
						continue;
					System.out.println((current) + " / "+all);
					GuangDongSpecFinanicalPDF2Struct_V1 gstruct= new GuangDongSpecFinanicalPDF2Struct_V1();
					try{
						String content = Word2Text.extract(f);
						gstruct.setContent(content);
						String fileName = f.getName();
						String[] fsplit =splitFileName(fileName);
						gstruct.setUuid(fsplit[0]);
						gstruct.setProject(fsplit[1].replace(".doc", "").replace(".docx", ""));
					}catch(Exception e){
						e.printStackTrace();
						continue;
					}
					if(gstruct.getContent().replaceAll(" ","").trim().length() > 200 || gstruct.getUuid() == null ){
						HashMap<String, Object> hm = gstruct.getMapKeyValue();
						String uuid = hm.get("uuid").toString(); 
						System.out.println(uuid);
						String hd5findename = StrUtils.toMd5Str(uuid);
						Put p = new Put((hd5findename).getBytes());
						for(String key:hm.keySet()){
							p.addColumn("a".getBytes(), key.getBytes(), hm.get(key).toString().getBytes());
						}
						puts.add(p);
						
//						System.out.println(gstruct.getContent());
						if(i <=0){
							hdao.put("GDSpecialFinancial", puts);
							System.out.println("put ---------");
							puts = new ArrayList<Put>();
							i = maxsize;
							}
					}
				}catch(Exception e){
						
						e.printStackTrace();
						continue;
					}
				}
				hdao.put("GDSpecialFinancial", puts);
			}catch(Exception e){
				e.printStackTrace();
			}finally{
				hdao.destory();
			}
	}

	
	/*提取pdf文件*/
	public static void pdfextract()
	{	
		HbaseDao hdao = new HbaseDao();
		try{
			File pdfdir = new File("E:\\专项资金\\uploads");
			File[] pdfs = pdfdir.listFiles(new FileFilter(){

				@Override
				public boolean accept(File pathname) {
					// TODO Auto-generated method stub
					try{
					if(pathname.getName().endsWith(".pdf") )
						return true;
					}catch(Exception e){
					}
					return false;
				}
				
			});
			List<Put> puts = new ArrayList<Put>();
			int maxsize = 100;
			int i = maxsize;
			for(File f : pdfs){
				try{
					System.out.println(f.getName());
					i-=1;
					GuangDongSpecFinanicalPDF2Html_V1 g = null;
					GuangDongSpecFinanicalPDF2Struct_V1 gstruct= null;
					try{
					 g = new GuangDongSpecFinanicalPDF2Html_V1(f.getPath());
					 gstruct = g.getExtraction();
					}catch(Exception e){
						e.printStackTrace();
						continue;
					}
					if(gstruct.getContent().replaceAll(" ","").trim().length() > 200 || gstruct.getUuid() == null ){
						HashMap<String, Object> hm = gstruct.getMapKeyValue();
						String uuid = hm.get("uuid").toString(); 
						String hd5findename = StrUtils.toMd5Str(uuid);
						Put p = new Put((hd5findename).getBytes());
						
						for(String key:hm.keySet()){
							p.addColumn("a".getBytes(), key.getBytes(), hm.get(key).toString().getBytes());
						}
						puts.add(p);
						System.out.println(hd5findename);
						System.out.println(gstruct.getContent());
						if(i <=0){
							hdao.put("GDSpecialFinancial", puts);
							System.out.println("put ---------");
							puts = new ArrayList<Put>();
							i = maxsize;
							}
					}
				}catch(Exception e){
						
						e.printStackTrace();
						continue;
					}
				}
				hdao.put("GDSpecialFinancial", puts);
			}catch(Exception e){
				e.printStackTrace();
			}finally{
				hdao.destory();
			}
	}
	
	public static void main(String args[])
	{
		SpecialFinanical_v1.wordextract();
	}
}
