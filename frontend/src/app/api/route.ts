import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { NextResponse } from "next/server";

// Configure the S3 Client to point to your local MinIO Docker
const s3Client = new S3Client({
  region: "us-east-1", // MinIO doesn't care, but AWS SDK requires a string here
  endpoint: process.env.MINIO_ENDPOINT || "http://127.0.0.1:9000",
  credentials: {
    accessKeyId: process.env.MINIO_ACCESS_KEY || "your-minio-user",
    secretAccessKey: process.env.MINIO_SECRET_KEY || "your-minio-password",
  },
  forcePathStyle: true, // 🚨 CRITICAL FOR MINIO: Forces path-style URLs instead of virtual-host style
});

export async function POST(req: Request) {
  try {
    const formData = await req.formData();
    const file = formData.get("file") as File;

    if (!file) {
      return NextResponse.json({ error: "No file received." }, { status: 400 });
    }

    const buffer = Buffer.from(await file.arrayBuffer());
    const fileName = `${Date.now()}-${file.name.replace(/\s/g, "-")}`;
    const bucketName = "my-lexical-images"; // Make sure you created this bucket in MinIO!

    // Upload to MinIO
    const command = new PutObjectCommand({
      Bucket: bucketName,
      Key: fileName,
      Body: buffer,
      ContentType: file.type,
    });

    await s3Client.send(command);

    // Construct the public URL to return to the editor
    // Note: Ensure your MinIO bucket is set to "Public" access policy in the MinIO console!
    const fileUrl = `${process.env.MINIO_ENDPOINT}/${bucketName}/${fileName}`;

    return NextResponse.json({ url: fileUrl });
  } catch (error) {
    console.error("Error uploading to MinIO:", error);
    return NextResponse.json({ error: "Upload failed" }, { status: 500 });
  }
}