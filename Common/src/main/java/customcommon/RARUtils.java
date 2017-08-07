package customcommon;

import com.github.junrar.extract.ExtractArchive;

import java.io.File;

public class RARUtils{
    public RARUtils(){

    }
    public void extract(String rarFilePath, String outDir){
        final File rar = new File(rarFilePath);
        final File destinationFolder = new File(outDir);
        ExtractArchive extractArchive = new ExtractArchive();
        extractArchive.extractArchive(rar, destinationFolder);
    }

    public static void main(String args[]){
        RARUtils au = new RARUtils();
        au.extract("D:\\tmp\\传统文学类.rar","D:\\tmp\\dfd");
    }
}