package customcommon;

import lumag.chm.CHMReader;
import lumag.chm.CommonReader;
import lumag.chm.FileFormatException;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;

/**
 * Created by gxkj-941 on 2017/4/5.
 */
public class FunctionsFiles {
    public static void main(String args[]){
        RARUtils ru = new RARUtils();
        FileUtils fu = new FileUtils();
        String inputPath1 = "D:\\tmp\\function_files";
        String out1 = "D:\\tmp\\function_htmls";
        try{
            File[] f1s = fu.fileList(inputPath1);
            for(File f :f1s){
                try {
//                ru.extract(f.getPath(),out1);
                    String name = f.getPath();
                    String title = name.substring(name.lastIndexOf("\\"), name.lastIndexOf(".")) + "_";
                    System.out.println(title);
                    CommonReader reader = new CHMReader(name);
                    reader.dump(out1, title);
                }catch (IOException e){}
                catch(FileFormatException e){}
            }
        }catch (FileNotFoundException e){
            e.printStackTrace();
        }
    }
}
