package customcommon;

import java.io.File;
import java.io.FileFilter;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.List;
import java.io.BufferedReader;
import java.io.FileReader;
/**
 * Created by gxkj-941 on 2017/4/5.
 */
public class FileUtils {
    public File[] fileList(String path) throws FileNotFoundException{
        List<String> files = new ArrayList<String>();
        File f = new File(path);
        FileFilter ff = new FileFilter() {
            @Override
            public boolean accept(File pathname) {
                if(pathname.isFile()) {
                    return true;
                }
                return false;
            }
        };
        File[] ffs = f.listFiles(ff);
        return ffs;
    }
    
    public static BufferedReader getFile2BuffRead(String path) throws FileNotFoundException{
    	  
    	 return getFile2BuffRead(new File(path));
    }
    
    public static BufferedReader getFile2BuffRead(File file) throws FileNotFoundException{
   	 FileReader fr = new FileReader(file);
   	 BufferedReader bff = new BufferedReader(fr);
   	 return bff;
   }
    
        
    public List<String> findAllDirectorys(String path){
        List<String> files = new ArrayList<String>();
        File f = new File(path);
        FileFilter ff = new FileFilter() {
            @Override
            public boolean accept(File pathname) {
                if(pathname.isDirectory()) {
                        return true;
                }
                return false;
            }
        };
        File[] ffs = f.listFiles(ff);
        for(File subF :ffs){
            files.add(subF.getPath());
            files.addAll(findAllDirectorys(subF.getPath()));
        }
        return files;
    }
    public static void main(String args[]){
        FileUtils fu = new FileUtils();
        List<String> files = fu.findAllDirectorys("D:\\tmp\\rar_files");
        try {
            for (String s : files) {
                File[] fz = fu.fileList(s);
                for(File f :fz){
                    System.out.println(f.getPath());
                }
            }
        }catch (FileNotFoundException fe){

        }
    }
}
