/**
 * 
 */
package lumag.crypto.ms;

import lumag.util.CipherAdapter;

import javax.crypto.BadPaddingException;
import javax.crypto.IllegalBlockSizeException;
import java.security.InvalidKeyException;
import java.security.Key;

public final class MsDesAdapter extends CipherAdapter {
	private MsDES des = new MsDES();

	@Override
	public void init(int opmode, Key key) throws InvalidKeyException {
		des.engineInit(opmode, key, null);
	}

	@Override
	public byte[] doFinal(byte[] data)
			throws IllegalBlockSizeException, BadPaddingException {
		return des.engineDoFinal(data, 0, data.length);
	}
}
