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
	private static final float MAX_WIDTH = 100;
	private static final float MAX_HEIGHT = 100;
	private final String JPG_TYPE = "jpg";
	private final String JPG_MIME = "image/jpeg";
	private final String PNG_TYPE = "png";
	private final String PNG_MIME = "image/png";

	public String handleRequest(S3Event s3event, Context context) {
		try {
			final S3EventNotificationRecord record = s3event.getRecords().get(0);

			final String srcBucket = record.getS3().getBucket().getName();
			// Object key may have spaces or unicode non-ASCII characters.
			String srcKey = record.getS3().getObject().getKey().replace('+', ' ');
			srcKey = URLDecoder.decode(srcKey, "UTF-8");

			final String dstBucket = "bbr-media-upload-thumbnail";
			final String dstKey = srcKey;

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
			final String imageType = matcher.group(1);
			if (!this.JPG_TYPE.equals(imageType) && !this.PNG_TYPE.equals(imageType)) {
				System.out.println("Skipping non-image " + srcKey);
				return "";
			}

			// Download the image from S3 into a stream
			final AmazonS3 s3Client = AmazonS3ClientBuilder.standard().build();
			final S3Object s3Object = s3Client.getObject(new GetObjectRequest(srcBucket, srcKey));
			final InputStream objectData = s3Object.getObjectContent();

			// Read the source image
			final BufferedImage srcImage = ImageIO.read(objectData);
			final int srcHeight = srcImage.getHeight();
			final int srcWidth = srcImage.getWidth();
			// Infer the scaling factor to avoid stretching the image
			// unnaturally
			final float scalingFactor = Math.min(CreateThumbnail.MAX_WIDTH / srcWidth,
					CreateThumbnail.MAX_HEIGHT / srcHeight);
			final int width = (int) (scalingFactor * srcWidth);
			final int height = (int) (scalingFactor * srcHeight);

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
			ImageIO.write(resizedImage, imageType, os);
			final InputStream is = new ByteArrayInputStream(os.toByteArray());
			// Set Content-Length and Content-Type
			final ObjectMetadata meta = new ObjectMetadata();
			meta.setContentLength(os.size());
			if (this.JPG_TYPE.equals(imageType)) {
				meta.setContentType(this.JPG_MIME);
			}
			if (this.PNG_TYPE.equals(imageType)) {
				meta.setContentType(this.PNG_MIME);
			}

			// Uploading to S3 destination bucket
			System.out.println("Writing to: " + dstBucket + "/" + dstKey);
			s3Client.putObject(dstBucket, dstKey, is, meta);
			System.out.println("Successfully resized " + srcBucket + "/" + srcKey + " and uploaded to " + dstBucket
					+ "/" + dstKey);
			return "Ok";
		} catch (final IOException e) {
			throw new RuntimeException(e);
		}
	}
}