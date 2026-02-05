#!/bin/bash

# ============================================================================
# Aster Support Bot - KMS Secret Fetcher
# 阿里云 Telegram 支持机器人 - KMS 密钥获取脚本
#
# Description | 描述:
# This script fetches secrets from Aliyun KMS/Secrets Manager and 
# populates the environment file for the service.
# 此脚本从阿里云 KMS/Secrets Manager 获取密钥并填充服务的环境变量文件。
#
# Security Requirements | 安全要求:
# - Must run as root (called by systemd ExecStartPre)
# - 必须以 root 运行（由 systemd ExecStartPre 调用）
# - Permissions: 700, owner root:root
# - 权限：700，所有者 root:root
# - Never prints secrets to stdout/stderr
# - 永不将密钥打印到 stdout/stderr
#
# Expected KMS Secret JSON Structure | 期望的 KMS 密钥 JSON 结构:
# {
#   "TELEGRAM_BOT_TOKEN": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
#   "STAFF_GROUP_ID": "-1001234567890",
#   "ADMIN_USER_ID": "123456789"
# }
# ============================================================================

set -euo pipefail

# Configuration | 配置
ENV_FILE="/etc/aster-support-bot/aster-support-bot.env"
ENV_DIR="$(dirname "${ENV_FILE}")"
REQUIRED_TOOLS=("jq" "aliyun")

# Colors for output | 输出颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================================
# Functions | 函数
# ============================================================================

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must run as root | 此脚本必须以 root 运行"
        exit 1
    fi
}

check_required_tools() {
    local missing_tools=()
    
    for tool in "${REQUIRED_TOOLS[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Required tools missing | 缺少必需工具: ${missing_tools[*]}"
        log_error "Please install: jq, aliyun-cli"
        log_error "请安装: jq, aliyun-cli"
        exit 1
    fi
}

check_env_vars() {
    if [[ -z "${KMS_SECRET_NAME:-}" ]]; then
        log_error "KMS_SECRET_NAME environment variable not set"
        log_error "KMS_SECRET_NAME 环境变量未设置"
        exit 1
    fi
    
    if [[ -z "${KMS_REGION_ID:-}" ]]; then
        log_error "KMS_REGION_ID environment variable not set"
        log_error "KMS_REGION_ID 环境变量未设置"
        exit 1
    fi
}

fetch_secret_from_kms() {
    local secret_name="$1"
    local region_id="$2"
    local version_id="${3:-}"
    
    log_info "Fetching secret from KMS | 从 KMS 获取密钥..."
    log_info "Secret Name: ${secret_name}"
    log_info "Region: ${region_id}"
    
    local cmd=(
        aliyun kms GetSecretValue
        --SecretName "${secret_name}"
        --RegionId "${region_id}"
    )
    
    # Add version if specified | 如果指定则添加版本
    if [[ -n "${version_id}" ]]; then
        cmd+=(--VersionId "${version_id}")
        log_info "Version: ${version_id}"
    else
        log_info "Version: latest | 最新版本"
    fi
    
    cmd+=(--query SecretData --output text)
    
    # Execute command and capture output | 执行命令并捕获输出
    # DO NOT echo the result, it contains secrets! | 不要 echo 结果，它包含密钥！
    local secret_json
    if ! secret_json=$("${cmd[@]}" 2>&1); then
        log_error "Failed to fetch secret from KMS"
        log_error "从 KMS 获取密钥失败"
        log_error "Command output (sanitized): Failed to call aliyun CLI"
        exit 1
    fi
    
    if [[ -z "${secret_json}" ]]; then
        log_error "Empty secret returned from KMS"
        log_error "从 KMS 返回的密钥为空"
        exit 1
    fi
    
    echo "${secret_json}"
}

parse_and_validate_json() {
    local json="$1"
    
    # Validate JSON | 验证 JSON
    if ! echo "${json}" | jq empty 2>/dev/null; then
        log_error "Invalid JSON format in secret"
        log_error "密钥中的 JSON 格式无效"
        exit 1
    fi
    
    # Extract required fields | 提取必需字段
    local token staff_group admin_user
    
    token=$(echo "${json}" | jq -r '.TELEGRAM_BOT_TOKEN // empty')
    staff_group=$(echo "${json}" | jq -r '.STAFF_GROUP_ID // empty')
    admin_user=$(echo "${json}" | jq -r '.ADMIN_USER_ID // empty')
    
    # Validate all fields are present | 验证所有字段都存在
    if [[ -z "${token}" ]]; then
        log_error "TELEGRAM_BOT_TOKEN missing in secret"
        log_error "密钥中缺少 TELEGRAM_BOT_TOKEN"
        exit 1
    fi
    
    if [[ -z "${staff_group}" ]]; then
        log_error "STAFF_GROUP_ID missing in secret"
        log_error "密钥中缺少 STAFF_GROUP_ID"
        exit 1
    fi
    
    if [[ -z "${admin_user}" ]]; then
        log_error "ADMIN_USER_ID missing in secret"
        log_error "密钥中缺少 ADMIN_USER_ID"
        exit 1
    fi
    
    # Return values as space-separated string | 以空格分隔的字符串返回值
    echo "${token}|${staff_group}|${admin_user}"
}

write_env_file_atomic() {
    local token="$1"
    local staff_group="$2"
    local admin_user="$3"
    
    log_info "Writing environment file | 写入环境变量文件..."
    
    # Create directory if not exists | 如果不存在则创建目录
    mkdir -p "${ENV_DIR}"
    
    # Create temporary file | 创建临时文件
    local tmp_file
    tmp_file=$(mktemp "${ENV_DIR}/.env.XXXXXX")
    
    # Write content to temporary file | 将内容写入临时文件
    cat > "${tmp_file}" <<EOF
# Auto-generated by aster-support-bot-fetch-secrets.sh
# 由 aster-support-bot-fetch-secrets.sh 自动生成
# Generated at: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
# DO NOT EDIT MANUALLY | 不要手动编辑

TELEGRAM_BOT_TOKEN=${token}
STAFF_GROUP_ID=${staff_group}
ADMIN_USER_ID=${admin_user}
ENV=prod
EOF
    
    # Set proper permissions before moving | 移动前设置正确的权限
    chmod 600 "${tmp_file}"
    chown root:root "${tmp_file}"
    
    # Atomic move | 原子移动
    mv "${tmp_file}" "${ENV_FILE}"
    
    log_info "Environment file updated successfully"
    log_info "环境变量文件更新成功"
    log_info "File: ${ENV_FILE}"
    log_info "Permissions: $(stat -c '%a %U:%G' "${ENV_FILE}" 2>/dev/null || stat -f '%p %Su:%Sg' "${ENV_FILE}")"
}

# ============================================================================
# Main Execution | 主执行流程
# ============================================================================

main() {
    log_info "=== Aster Support Bot - Secret Fetcher ==="
    log_info "=== 阿里云支持机器人 - 密钥获取器 ==="
    
    # Step 1: Verify running as root | 步骤1：验证以 root 运行
    check_root
    
    # Step 2: Check required tools | 步骤2：检查必需工具
    check_required_tools
    
    # Step 3: Check environment variables | 步骤3：检查环境变量
    check_env_vars
    
    # Step 4: Fetch secret from KMS | 步骤4：从 KMS 获取密钥
    local secret_json
    secret_json=$(fetch_secret_from_kms \
        "${KMS_SECRET_NAME}" \
        "${KMS_REGION_ID}" \
        "${KMS_VERSION_ID:-}")
    
    # Step 5: Parse and validate JSON | 步骤5：解析并验证 JSON
    local parsed
    parsed=$(parse_and_validate_json "${secret_json}")
    
    IFS='|' read -r token staff_group admin_user <<< "${parsed}"
    
    # Step 6: Write environment file atomically | 步骤6：原子写入环境变量文件
    write_env_file_atomic "${token}" "${staff_group}" "${admin_user}"
    
    log_info "=== Secret fetch completed successfully ==="
    log_info "=== 密钥获取成功完成 ==="
}

# Execute main function | 执行主函数
main "$@"
