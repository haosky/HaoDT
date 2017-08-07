package entity;

import com.alibaba.fastjson.annotation.JSONField;

public class Juece {
	@JSONField(name = "bt")
	private String bt;
	@JSONField(name = "namedentity")
	private String namedentity;
	@JSONField(name = "nr")
	private String nr;
	@JSONField(name = "docid")
	private long docid;
	@JSONField(name = "strId")
	private String strid;
	@JSONField(name = "docchannel")
	private long docchannel;
	@JSONField(name = "topic_name")
	private String topicName;
	@JSONField(name = "laiyuan")
	private String laiyuan;
	@JSONField(name = "riqi")
	private String riqi;
	@JSONField(name = "_id")
	private String id;
	@JSONField(name = "topic_id")
	private String topicId;
	@JSONField(name = "dataset")
	private String dataset;

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

	public String getNr() {
		return nr;
	}
	public void setNr(String nr) {
		this.nr = nr;
	}

	public long getDocid() {
		return docid;
	}
	public void setDocid(long docid) {
		this.docid = docid;
	}

	public String getStrid() {
		return strid;
	}
	public void setStrid(String strid) {
		this.strid = strid;
	}

	public long getDocchannel() {
		return docchannel;
	}
	public void setDocchannel(long docchannel) {
		this.docchannel = docchannel;
	}

	public String getTopicName() {
		return topicName;
	}
	public void setTopicName(String topicName) {
		this.topicName = topicName;
	}

	public String getLaiyuan() {
		return laiyuan;
	}
	public void setLaiyuan(String laiyuan) {
		this.laiyuan = laiyuan;
	}

	public String getRiqi() {
		return riqi;
	}
	public void setRiqi(String riqi) {
		this.riqi = riqi;
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
