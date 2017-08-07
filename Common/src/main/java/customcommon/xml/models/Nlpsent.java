package customcommon.xml.models;
import customcommon.xml.models.Nlparg;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
public class Nlpsent {
	private int id;
	private String cont;
	private List<Nlpword> word;
	public Nlpsent(){
		if(word ==null)
		word = new ArrayList<Nlpword>();
	}
	
	public void setId(int id){
		this.id = id;
	}
	
	public void addWord(Nlpword word){
		try{	
		if(word !=null)
			this.word.add(word);
		}catch(Exception e){
			e.printStackTrace();
		}
		 
	}
	
	public void setCont(String cont){
		this.cont = cont;
	}
	
	 
	public int getId(){
		return this.id;
	}
	
	public String getCont(){
		return this.cont;
	} 
	public Iterator getWord(){
		return this.word.iterator();
	}
	
	public Nlpword findArg( int id ){
		for(Nlpword word : this.word){
			if(word.getId() == id){
				return word;
			}
		}
		return null;
	}
	
	public List<Nlpword> getWordAsList(){
		return this.word;
	}
}
