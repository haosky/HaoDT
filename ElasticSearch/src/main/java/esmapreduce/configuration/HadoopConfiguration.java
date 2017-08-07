package esmapreduce.configuration;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.io.MapWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.elasticsearch.hadoop.mr.EsOutputFormat;
import org.apache.hadoop.io.NullWritable;
 

public class HadoopConfiguration {
	
	public static Job configureJob(Configuration conf,String esresource)
			 throws IOException, ClassNotFoundException, InterruptedException {
			   Job job = Job.getInstance(conf);
			   job.setSpeculativeExecution(false);    
			   Properties prop = new Properties();
			   InputStream ins = HadoopConfiguration.class.getClassLoader().getResourceAsStream("elasticsearchSettings.properties");
			   prop.load(ins);
			   conf.set("es.nodes", prop.getProperty("es.nodes"));
			   conf.set("es.resource", esresource);
			   
			   // ndicate the input for EsOutputFormat is of type JSON.
			   conf.set("es.input.json", "yes");        
			   job.setMapOutputValueClass(Text.class); 
			   job.setOutputFormatClass(EsOutputFormat.class);
			   job.setOutputKeyClass(NullWritable.class); 
			   job.waitForCompletion(true);
			   return job;
			 }
	
	public static Job configureJob(Job job,String esresource)
			 throws IOException, ClassNotFoundException, InterruptedException {
			   Configuration conf = job.getConfiguration();
			   job.setSpeculativeExecution(false);    
			   Properties prop = new Properties();
			   InputStream ins = HadoopConfiguration.class.getClassLoader().getResourceAsStream("elasticsearchSettings.properties");
			   prop.load(ins);
			   conf.set("es.nodes", prop.getProperty("es.nodes"));
			   conf.set("es.resource", esresource);
			   
			   // ndicate the input for EsOutputFormat is of type JSON.
			   conf.set("es.input.json", "yes");        
			   job.setMapOutputValueClass(Text.class); 
			   job.setOutputFormatClass(EsOutputFormat.class);
//			   job.setOutputKeyClass(NullWritable.class);
			   job.waitForCompletion(true);
			   return job;
			 }

}
