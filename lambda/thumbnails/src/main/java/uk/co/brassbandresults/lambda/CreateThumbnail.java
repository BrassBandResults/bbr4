package uk.co.brassbandresults.lambda;

import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URLDecoder;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import javax.imageio.ImageIO;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.S3Event;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.event.S3EventNotification.S3EventNotificationRecord;
import com.amazonaws.services.s3.model.GetObjectRequest;
import com.amazonaws.services.s3.model.ObjectMetadata;
import com.amazonaws.services.s3.model.S3Object;

public class CreateThumbnail implements RequestHandler<S3Event, String> {

	// Profile Pictures
	// - homepage 72x72
	// - profile page 200x200

	// Programme Covers
	// - wall of shame 72-80x100
	// - full size - 462x663

	// Programme page
	// - list - 80x56
	// - full size - 800x565

	// thumb - 100x100 max
	// full size profile - 200x200 max
	// full size programme page - 800x800

	// All images get resized to fit within
	// WxH
	// 70x70
	// 100x100
	// 200x200
	// 800x1200

	private static final List<Dimensions> dimensions = Arrays.asList( //
			new Dimensions(70, 70), //
			new Dimensions(100, 100), //
			new Dimensions(200, 200), //
			new Dimensions(800, 1200) //
	);

	static {
		CreateThumbnail.mimeType = new HashMap<>();
		CreateThumbnail.mimeType.put("jpg", "image/jpeg");
		CreateThumbnail.mimeType.put("jpeg", "image/jpeg");
		CreateThumbnail.mimeType.put("png", "image/png");
		CreateThumbnail.mimeType.put("gif", "image/gif");
		CreateThumbnail.mimeType.put("bmp", "image/bmp");
	}

	private static HashMap<String, String> mimeType;

	@Override
	public String handleRequest(S3Event s3event, Context context) {
		try {
			final S3EventNotificationRecord record = s3event.getRecords().get(0);

			final String srcBucket = record.getS3().getBucket().getName();
			// Object key may have spaces or unicode non-ASCII characters.
			String srcKey = record.getS3().getObject().getKey().replace('+', ' ');
			srcKey = URLDecoder.decode(srcKey, "UTF-8");

			final String dstBucket = "bbr-media-upload-thumbnail";

			// Sanity check: validate that source and destination are different
			// buckets.
			if (srcBucket.equals(dstBucket)) {
				System.out.println("Destination bucket must not match source bucket.");
				return "";
			}

			// Infer the image type.
			final Matcher matcher = Pattern.compile(".*\\.([^\\.]*)").matcher(srcKey);
			if (!matcher.matches()) {
				System.out.println("Unable to infer image type for key " + srcKey);
				return "";
			}
			final String imageExtension = matcher.group(1);
			final String imageTypeLower = imageExtension.toLowerCase();
			final String mimeType = CreateThumbnail.mimeType.get(imageTypeLower);
			System.out.println("Image extension is " + imageExtension);
			if (mimeType == null) {
				System.out.println("Skipping non-image " + srcKey);
				return "";
			} else {
				System.out.println("Mime Type is " + mimeType);
			}

			// Download the image from S3 into a stream
			final AmazonS3 s3Client = AmazonS3ClientBuilder.standard().build();
			final S3Object s3Object = s3Client.getObject(new GetObjectRequest(srcBucket, srcKey));

			// Read the source image
			final InputStream objectData = s3Object.getObjectContent();
			final BufferedImage srcImage = ImageIO.read(objectData);
			final int srcHeight = srcImage.getHeight();
			final int srcWidth = srcImage.getWidth();
			System.out.println("  - Source WxH " + srcWidth + "x" + srcHeight);

			for (final Dimensions dim : CreateThumbnail.dimensions) {

				System.out.print("Resizing to fit within WxH" + dim.getWidth() + "x" + dim.getHeight());

				// Infer the scaling factor to avoid stretching the image unnaturally
				final float scalingFactor = Math.min((float) dim.getWidth() / srcWidth, (float) dim.getHeight() / srcHeight);
				System.out.println("  - Scaling Factor " + scalingFactor);
				final int potentialWidth = (int) (scalingFactor * srcWidth);
				final int width = potentialWidth <= 0 ? srcWidth : potentialWidth;
				final int potentialHeight = (int) (scalingFactor * srcHeight);
				final int height = potentialHeight <= 0 ? srcHeight : potentialHeight;
				System.out.println("  - Destination WxH " + width + "x" + height);

				final BufferedImage resizedImage = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
				final Graphics2D g = resizedImage.createGraphics();
				// Fill with white before applying semi-transparent (alpha) images
				g.setPaint(Color.white);
				g.fillRect(0, 0, width, height);
				// Simple bilinear resize
				// If you want higher quality algorithms, check this link:
				// https://today.java.net/pub/a/today/2007/04/03/perils-of-image-getscaledinstance.html
				g.setRenderingHint(RenderingHints.KEY_INTERPOLATION, RenderingHints.VALUE_INTERPOLATION_BILINEAR);
				g.drawImage(srcImage, 0, 0, width, height, null);
				g.dispose();

				// Re-encode image to target format
				final ByteArrayOutputStream os = new ByteArrayOutputStream();
				ImageIO.write(resizedImage, imageTypeLower, os);
				final InputStream is = new ByteArrayInputStream(os.toByteArray());
				// Set Content-Length and Content-Type
				final ObjectMetadata meta = new ObjectMetadata();
				meta.setContentLength(os.size());
				meta.setContentType(mimeType);

				// Uploading to S3 destination bucket
				final String dstKey = srcKey + dim.getSuffix() + "." + imageExtension;
				System.out.println("  - Writing to: " + dstBucket + "/" + dstKey);
				s3Client.putObject(dstBucket, dstKey, is, meta);
				System.out.println("  - Successfully resized " + srcBucket + "/" + srcKey + " and uploaded to " + dstBucket + "/" + dstKey);
			}
			return "Ok";
		} catch (final IOException e) {
			throw new RuntimeException(e);
		}
	}
}