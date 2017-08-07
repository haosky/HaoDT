package customcommon.xml.models;

import java.util.List;

public class Nlparg {
	private int id;
	private String type;
	private int beg;
	private int end;
	
	public void setId(int id){
		this.id = id;
	}
	
	public void setType(String type){
		this.type = type;
	}
	
	public void setBeg(int beg){
		this.beg = beg;
	}
	
	public void setEnd(int end){
		this.end = end;
	}
	
	public int getId(){
		return id;
	}
	
	public String getType(){
		return this.type;
	}
	
	public int getBeg(){
		return this.beg;
	}
	
	public int getEnd(){
		return this.end;
	}
	
	
}
