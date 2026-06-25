/// <reference path="./.sst/platform/config.d.ts" />

export default $config({
  app(input) {
    return {
      name: "cardly-backend",
      removal: input?.stage === "prod" ? "retain" : "remove",
      protect: ["prod"].includes(input?.stage),
      home: "aws",
      providers: {
        gcp: {
          version: "8.0.0",
          project: "cardly-learn"
        }
      }
    };
  },
  async run() {
    const gcp = await import("@pulumi/gcp");
    // 1. Lấy tên stage hiện tại
    const stage = $app.stage;

    // 2. Tạo các biến logic (true/false) để dễ kiểm tra
    const isProd = stage === "prod";
    const isStaging = stage === "staging";

    const countCpu = isProd ? 1 : 1;
    const countMemory = isProd ? "1024Mi" : "512Mi";
    
    // Nơi code tài nguyên GCP sẽ nằm ở đây...
    // 3. Khai báo Cloud Run Service
    const myService = new gcp.cloudrunv2.Service("cardly-api", {
      location: "asia-southeast1", // Chọn region gần VN nhất (Singapore)
      template: {
        containers: [{
          image: "asia-southeast1-docker.pkg.dev/cardly-learn/cardly-learn/cardly-backend:3284d1bbd38bb806b5a65015cc32f386372f2f84",
          ports: { containerPort: 8080 },
          args: ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"],
          envs: [
            { name: "MONGO_URI", value: process.env.MONGO_URI || "" },
            { name: "DB_NAME", value: process.env.DB_NAME || "" },
            { name: "GEMINI_API_KEY", value: process.env.GEMINI_API_KEY || "" },
            { name: "AWS_S3_BUCKET", value: process.env.AWS_S3_BUCKET || "" },
            { name: "AWS_S3_REGION", value: process.env.AWS_S3_REGION || "" }
          ],
          resources: {
            // Nếu là Prod thì dùng RAM lớn hơn, test thì dùng RAM nhỏ để tiết kiệm
            limits: {
              memory: isProd ? "1024Mi" : "512Mi",
              cpu: isProd ? "1" : "1",
            }
          }
        }],
        scaling: {
          maxInstanceCount: isProd ? 5 : 1, // Prod cho phép scale tối đa 5 server
        }
      },
    });

    // 4. Mở quyền Public để ai cũng có thể truy cập qua trình duyệt
    new gcp.cloudrunv2.ServiceIamPolicy("public-access", {
      location: myService.location,
      project: myService.project,
      name: myService.name,
      policyData: JSON.stringify({
        bindings: [{
          role: "roles/run.invoker",
          members: ["allUsers"], // Cho phép toàn bộ người dùng Internet truy cập
        }],
      }),
    });

    // 5. Xuất đường link URL của Cloud Run ra màn hình Terminal
    return {
      ApiUrl: myService.uri,
    };
  },
});
