package entity;

import com.alibaba.fastjson.annotation.JSONField;

public class Jyya {
	@JSONField(name = "collectTime")
	private String collecttime;
	@JSONField(name = "nav")
	private String nav;
	@JSONField(name = "nr")
	private String nr;
	@JSONField(name = "DBID")
	private int dbid;
	@JSONField(name = "strId")
	private String strid;
	@JSONField(name = "daibiaos")
	private String daibiaos;
	@JSONField(name = "JYID")
	private long jyid;
	@JSONField(name = "pic")
	private String pic;
	@JSONField(name = "uploadTime")
	private String uploadtime;
	@JSONField(name = "type")
	private String type;
	@JSONField(name = "url")
	private String url;
	@JSONField(name = "HYID")
	private String hyid;
	@JSONField(name = "CBDWS")
	private String cbdws;
	@JSONField(name = "bt")
	private String bt;
	@JSONField(name = "NamedEntity")
	private String namedentity;
	@JSONField(name = "JYBH")
	private String jybh;
	@JSONField(name = "topic_name")
	private String topicName;
	@JSONField(name = "_id")
	private String id;
	@JSONField(name = "topic_id")
	private String topicId;
	@JSONField(name = "dataset")
	private String dataset;

	public String getCollecttime() {
		return collecttime;
	}
	public void setCollecttime(String collecttime) {
		this.collecttime = collecttime;
	}

	public String getNav() {
		return nav;
	}
	public void setNav(String nav) {
		this.nav = nav;
	}

	public String getNr() {
		return nr;
	}
	public void setNr(String nr) {
		this.nr = nr;
	}

	public int getDbid() {
		return dbid;
	}
	public void setDbid(int dbid) {
		this.dbid = dbid;
	}

	public String getStrid() {
		return strid;
	}
	public void setStrid(String strid) {
		this.strid = strid;
	}

	public String getDaibiaos() {
		return daibiaos;
	}
	public void setDaibiaos(String daibiaos) {
		this.daibiaos = daibiaos;
	}

	public long getJyid() {
		return jyid;
	}
	public void setJyid(long jyid) {
		this.jyid = jyid;
	}

	public String getPic() {
		return pic;
	}
	public void setPic(String pic) {
		this.pic = pic;
	}

	public String getUploadtime() {
		return uploadtime;
	}
	public void setUploadtime(String uploadtime) {
		this.uploadtime = uploadtime;
	}

	public String getType() {
		return type;
	}
	public void setType(String type) {
		this.type = type;
	}

	public String getUrl() {
		return url;
	}
	public void setUrl(String url) {
		this.url = url;
	}

	public String getHyid() {
		return hyid;
	}
	public void setHyid(String hyid) {
		this.hyid = hyid;
	}

	public String getCbdws() {
		return cbdws;
	}
	public void setCbdws(String cbdws) {
		this.cbdws = cbdws;
	}

	public String getBt() {
		return bt;
	}
	public void setBt(String bt) {
		this.bt = bt;
	}

	public String getNamedentity() {
		return namedentity;
	}
	public void setNamedentity(String namedentity) {
		this.namedentity = namedentity;
	}

	public String getJybh() {
		return jybh;
	}
	public void setJybh(String jybh) {
		this.jybh = jybh;
	}

	public String getTopicName() {
		return topicName;
	}
	public void setTopicName(String topicName) {
		this.topicName = topicName;
	}

	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}

	public String getTopicId() {
		return topicId;
	}
	public void setTopicId(String topicId) {
		this.topicId = topicId;
	}

	public String getDataset() {
		return dataset;
	}
	public void setDataset(String dataset) {
		this.dataset = dataset;
	}

}
