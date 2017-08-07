package crawler.contentextractor.webcollector;

import org.apache.commons.codec.binary.Hex;
import org.bouncycastle.jce.provider.BouncyCastleProvider;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.security.Security;
import java.util.Random;

/**
 * AES算法加密/解密工具类。
 * 
 */
public class AESUtil {
	//用的是CBC-256, 需用lib里的(1.7版)local_policy.jar和US_export_policy.jar替换JDK \jre\lib\security 里的文件
	private static final String ALGORITHM = "AES/CBC/PKCS5Padding";
	private static final String RANDOMSTR ="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz";
	

	/*****
	 * 对称加密方法
	 * @param byteData 待加密数据
	 * @param pass 密钥
	 * @param iv 对应表
	 * @return 加密后的数据
	 */
	public static byte[] encrypt(byte[] byteData, byte[] pass, byte[] iv) {
        try {
            //根据给定的字节数组构造一个密钥
            SecretKeySpec key = new SecretKeySpec(pass, "AES");
            Security.addProvider(new BouncyCastleProvider());
            
            //创建一个实现指定转换的 Cipher对象，该转换由指定的提供程序提供。
            Cipher cipher = Cipher.getInstance(ALGORITHM);
            cipher.init(Cipher.ENCRYPT_MODE, key, new IvParameterSpec(iv));
            
            byte[] encrypted = cipher.doFinal(byteData);

            return encrypted;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
	
	/*****
	 * 对称加密方法
	 * @param byteData 待加密数据
	 * @param pass 密钥
	 * @param iv 对应表
	 * @return 加密后的数据
	 */
	public static String encryptToStr(byte[] byteData, byte[] pass, byte[] iv) {
		try {
			//根据给定的字节数组构造一个密钥
			SecretKeySpec key = new SecretKeySpec(pass, "AES");
			Security.addProvider(new BouncyCastleProvider());
			
			//创建一个实现指定转换的 Cipher对象，该转换由指定的提供程序提供。
			Cipher cipher = Cipher.getInstance(ALGORITHM);
			cipher.init(Cipher.ENCRYPT_MODE, key, new IvParameterSpec(iv));
			
			byte[] encrypted = cipher.doFinal(byteData);
			
			return new String(Hex.encodeHex(encrypted));
		} catch (Exception e) {
			e.printStackTrace();
		}
		return null;
	}

	/*********
	 * 对称解密方法
	 * @param byteData 待解密数据
	 * @param pass 密钥
	 * @param iv 对应表
	 * @return 解密后的数据
	 */
    public static String decryptToStr(String encrypttext, byte[] pass, byte[] iv){
        try {
            SecretKeySpec key = new SecretKeySpec(pass, "AES");
            Security.addProvider(new BouncyCastleProvider());
            
            Cipher cipher = Cipher.getInstance(ALGORITHM);
            cipher.init(Cipher.DECRYPT_MODE, key, new IvParameterSpec(iv));
            
            byte[] en_data = Hex.decodeHex(encrypttext.toCharArray());
            byte[] orignal =cipher.doFinal(en_data);
            
            return new String(orignal);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    
    /*********
     * 对称解密方法
     * @param byteData 待解密数据
     * @param pass 密钥
     * @param iv 对应表
     * @return 解密后的数据
     */
    public static byte[] decrypt(byte[] byteData, byte[] pass, byte[] iv){
    	try {
    		SecretKeySpec key = new SecretKeySpec(pass, "AES");
    		Security.addProvider(new BouncyCastleProvider());
    		
    		Cipher cipher = Cipher.getInstance(ALGORITHM);
    		cipher.init(Cipher.DECRYPT_MODE, key, new IvParameterSpec(iv));
    		
    		byte[] orignal =cipher.doFinal(byteData);
    		
    		return orignal;
    	} catch (Exception e) {
    		e.printStackTrace();
    	}
    	return null;
    }
 
    //使用指定的字符串生成秘钥
    public static byte[] getKeyByPass(String pass) throws Exception {
        KeyGenerator kgen = KeyGenerator.getInstance(ALGORITHM);
        //256：密钥生成参数；securerandom：密钥生成器的随机源
        SecureRandom securerandom = new SecureRandom(pass.getBytes());
        kgen.init(256, securerandom);
        //生成（对称）密钥  
        SecretKey secretKey = kgen.generateKey();

        //返回基本编码格式的密钥
        return secretKey.getEncoded();
    }
    
    //转成十六进制字符串
	public static String parseByte2HexStr(byte[] buf){
		StringBuffer sb = new StringBuffer();
        for (int i = 0; i < buf.length; i++) {
            String hex = Integer.toHexString(buf[i] & 0xFF);
            if (hex.length() == 1) {
                hex = '0' + hex;
            }
            sb.append(hex.toUpperCase());
        }
        return sb.toString();
	}
	
	//hash password with SHA-256
	public static byte[] toHash256Deal(String key){
		try {
            MessageDigest digester = MessageDigest.getInstance("SHA-256");
            digester.update(key.getBytes());
            byte[] hex =digester.digest();
            return hex;
        } catch (Exception e) {
            throw new RuntimeException(e.getMessage());
        }
	}
	
	public static String getRandomStr(int length){
		int randomlen =RANDOMSTR.length();
		StringBuffer sb =new StringBuffer("");
		for(int i =0;i<length;i++){
			int idx =new Random().nextInt(randomlen);
			sb.append(RANDOMSTR.charAt(idx));
		}
		return sb.toString();
	}
}
