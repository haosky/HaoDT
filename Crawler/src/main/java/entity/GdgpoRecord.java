package entity;

import com.alibaba.fastjson.annotation.JSONField;

public class GdgpoRecord {
	@JSONField(name = "pagesize")
	private int pagesize;
	
	@JSONField(name = "_id")
	private String id;

	@JSONField(name = "ftype")
	private String ftype;
	
	@JSONField(name = "url")
	private String url;
	
	public String getUrl() {
		return url;
	}
	public void setUrl(String url) {
		this.url = url;
	}
	public String getFtype() {
		return ftype;
	}
	public void setFtype(String ftype) {
		this.ftype = ftype;
	}

	public int getPagesize() {
		return pagesize;
	}
	public void setPagesize(int pagesize) {
		this.pagesize = pagesize;
	}

	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}


}
