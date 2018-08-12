package uk.co.brassbandresults.lambda;

public class Dimensions {
	private final int height;
	private final int width;

	public Dimensions(int width, int height) {
		this.height = height;
		this.width = width;
	}

	public int getHeight() {
		return this.height;
	}

	public String getSuffix() {
		return "-" + this.getWidth() + "x" + this.getHeight();
	}

	public int getWidth() {
		return this.width;
	}

}
