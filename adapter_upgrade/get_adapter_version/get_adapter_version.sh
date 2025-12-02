#!/bin/bash

CAN_INTERFACE="can0"
CANFD_SEND_ID="388"
CANFD_SEND_DATA="01"
CANFD_RECEIVE_ID="387"

RECORD_FLAG=true

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

send_request_canfd_data(){
        echo "sending request to Adapter Board. ID:0x$CANFD_SEND_ID, Data:$CANFD_SEND_DATA"

        while true; do
                sleep 1.5  # 控制发送频率
                ## FD mode
                # cansend $CAN_INTERFACE $CANFD_SEND_ID##0$CANFD_SEND_DATA
                ## can 2.0 mode
                cansend $CAN_INTERFACE $CANFD_SEND_ID#01$CANFD_SEND_DATA
        done
}

reverse_endian() {
    local hex_string="$1"
    local result=""
    for ((i=${#hex_string}-2; i>=0; i-=2)); do
        result="${result}${hex_string:i:2}"
    done
    echo "$result"
}
parse_canfd_data(){
        
        local record_file="data.log"

        if [[ ! -f "$record_file" ]]; then
                echo "错误: 当前目录下未找到 $log_file 文件"
                echo "请确保 data.log 文件存在于当前目录"
                exit 1
        fi

        local file_content=$(cat "$record_file")
        local continuius_data=$(echo "$file_content" | tr -d ' ')

        # echo "$continuius_data"

        # local test_txt1="${continuius_data:11:128}"
        # local test_txt2="${continuius_data:151:128}"
        # local test_txt3="${continuius_data:291:128}"
        # local test_txt4="${continuius_data:431:128}"
        # local test_txt5="${continuius_data:571:128}"
        # local test_txt6="${continuius_data:711:128}"
        # local test_txt7="${continuius_data:851:96}"

        # echo $test_txt1
        # echo $test_txt2
        # echo $test_txt3
        # echo $test_txt4
        # echo $test_txt5
        # echo $test_txt6
        # echo $test_txt7

        local confirm_header_1="${continuius_data:11:10}"
        local confirm_header_2="${continuius_data:151:10}"
        local confirm_header_3="${continuius_data:291:10}"
        local confirm_header_4="${continuius_data:431:10}"
        local confirm_header_5="${continuius_data:571:10}"
        local confirm_header_6="${continuius_data:711:10}"
        local confirm_header_7="${continuius_data:851:10}"

        # echo $confirm_header_1
        # echo $confirm_header_2
        # echo $confirm_header_3
        # echo $confirm_header_4
        # echo $confirm_header_5
        # echo $confirm_header_6
        # echo $confirm_header_7

        local device_uuid_part_1="${continuius_data:25:114}"
        local device_uuid_part_2="${continuius_data:165:14}"
        local device_uuid="${device_uuid_part_1}${device_uuid_part_2}"
        device_uuid="${device_uuid//20/}"
        device_uuid=$(reverse_endian "$device_uuid")

        local bootloader_version="${continuius_data:179:32}"
        bootloader_version="${bootloader_version//20/}"
        bootloader_version=$(reverse_endian "$bootloader_version")

        local bootloader_build_data="${continuius_data:211:32}"
        bootloader_build_data="${bootloader_build_data//20/}"
        bootloader_build_data=$(reverse_endian "$bootloader_build_data")
        real_bootloader_build_data=$(date -d "@$((0x$bootloader_build_data))" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)

        local software_version="${continuius_data:243:32}"
        software_version="${software_version//20/}"
        software_version=$(reverse_endian "$software_version")

        local software_build_data_part_1="${continuius_data:275:4}"
        local software_build_data_part_2="${continuius_data:305:28}"
        local software_build_data="${software_build_data_part_1}${software_build_data_part_2}"
        software_build_data="${software_build_data//20/}"
        software_build_data=$(reverse_endian "$software_build_data")
        real_software_build_data=$(date -d "@$((0x$software_build_data))" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)

        local hardware_version="${continuius_data:333:32}"
        hardware_version="${hardware_version//20/}"
        hardware_version=$(reverse_endian "$hardware_version")

        local hardware_build_data="${continuius_data:365:32}"
        hardware_build_data="${hardware_build_data//20/}"
        hardware_build_data=$(reverse_endian "$hardware_build_data")
        real_hardware_build_data=$(date -d "@$((0x$hardware_build_data))" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)

        # echo $device_uuid
        # echo $bootloader_version
        # echo $bootloader_build_data
        # echo $software_version
        # echo $software_build_data
        # echo $hardware_version
        # echo $hardware_build_data

        bootloader_version_major=$(( 0x${bootloader_version:0:2} ))
        bootloader_version_board_type=$(( 0x${bootloader_version:2:2} ))
        bootloader_version_hw=$(( 0x${bootloader_version:4:2} ))
        bootloader_version_minor=$(( 0x${bootloader_version:6:2} - 1 ))

        # 对software_version做同样的处理
        app_version_major=$(( 0x${software_version:0:2} ))
        app_version_board_type=$(( 0x${software_version:2:2} ))
        app_version_hw=$(( 0x${software_version:4:2} ))
        app_version_minor=$(( 0x${software_version:6:2} - 1 ))

        # 对hardware_version做同样的处理
        hw_version_major=$(( 0x${hardware_version:0:2} ))
        hw_version_board_type=$(( 0x${hardware_version:2:2} ))
        hw_version_hw=$(( 0x${hardware_version:4:2} ))
        hw_version_minor=$(( 0x${hardware_version:6:2} ))

        echo "设备ID: $device_uuid"
        echo "BootLoader 版本: $bootloader_version_major.$bootloader_version_board_type.$bootloader_version_hw.$bootloader_version_minor"
        echo "BootLoader 构建时间: $real_bootloader_build_data"
        echo "APP 版本: $app_version_major.$app_version_board_type.$app_version_hw.$app_version_minor"
        echo "APP 构建时间: $real_software_build_data"
        echo "Hardware 版本: $hw_version_major.$hw_version_board_type.$hw_version_hw.$hw_version_minor"
        echo "Hardware 构建时间: $real_bootloader_build_data"
}

cleanup() {
    if [ ! -z "$SEND_PID" ] && kill -0 "$SEND_PID" 2>/dev/null; then
        kill "$SEND_PID" 2>/dev/null
        wait "$SEND_PID" 2>/dev/null
    fi
}

main(){
        cd "$SCRIPT_DIR" || exit 1
        send_request_canfd_data&
        SEND_PID=$! 
        timeout 3 candump $CAN_INTERFACE | grep --line-buffered "$CAN_INTERFACE  $CANFD_RECEIVE_ID" > ./data.log
        sleep 2
        parse_canfd_data

        cleanup
}

trap cleanup EXIT INT TERM
main
