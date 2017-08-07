package customcommon;
import java.io.IOException;
import java.net.URI;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
/**
 * Created by gxkj-941 on 2017/4/6.
 */
public class HdfsUtils {

    public static void putHdfs(String hdfsOutFile,String localInputPath)throws IOException{
        Configuration conf = new Configuration();

        Path inputDir = new Path(localInputPath);
        Path hdfsfile = new Path(hdfsOutFile);

        FileSystem hdfs = FileSystem.get(URI.create(hdfsOutFile), conf);
        FileSystem local = FileSystem.getLocal(conf);
        FileStatus[] status = local.listStatus(inputDir);
        FSDataOutputStream out = hdfs.create(hdfsfile);
        for(int i = 0; i < status.length; i++) {
            FSDataInputStream in = local.open(status[i].getPath());
            byte buffer[] = new byte[256];
            int byteread = 0;
            while((byteread = in.read(buffer)) > 0) {
                out.write(buffer);
            }
            in.close();
        }
        out.close();
    }

    public static void main(String args[]) throws IOException{
        HdfsUtils.putHdfs("hdfs://gx.master:9210/everyone/abc","D:\\tmp\\function_htmls\\市场的二十二法则_4.htm");
    }
}
