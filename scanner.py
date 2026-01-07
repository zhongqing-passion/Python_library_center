'''
Author: 
Date: 2026-01-07 18:35:35
Last Modified by: 
Last Modified time: 
'''
import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import time

class BarcodeScanner:
    def scan_isbn(self):
        """
        打开摄像头，扫描条形码（EAN-13/ISBN）。
        返回扫描到的 ISBN 字符串。
        如果用户按 'q' 取消或无法打开摄像头，返回 None。
        """
        # 尝试打开默认摄像头
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("无法打开摄像头")
            return None

        found_isbn = None
        
        print("正在启动摄像头... 请将书籍背面的条形码对准摄像头。")
        print("按 'q' 键取消扫描。")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("无法接收摄像头画面")
                break

            barcode_data = None
                    
            # 转为灰度图，提高识别速度
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 多角度检测（支持竖向条码）
            # 很多书本是竖着放的，默认扫描无法识别。尝试 0度 -> 90度 -> 270度
            # 保持 symbols=[ZBarSymbol.EAN13] 以防止崩溃并专注识别 ISBN
            barcodes = decode(gray, symbols=[ZBarSymbol.EAN13])
            is_rotated = False
            
            if not barcodes:
                # 尝试顺时针旋转90度
                gray_rotated = cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE)
                barcodes = decode(gray_rotated, symbols=[ZBarSymbol.EAN13])
                if barcodes:
                    is_rotated = True
            
            if not barcodes:
                # 尝试逆时针旋转90度
                gray_rotated = cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE)
                barcodes = decode(gray_rotated, symbols=[ZBarSymbol.EAN13])
                if barcodes:
                    is_rotated = True

            for barcode in barcodes:
                # 提取条形码数据
                barcode_data = barcode.data.decode("utf-8")
                barcode_type = barcode.type
                text = f"{barcode_data} ({barcode_type})"

                if not is_rotated:
                    # 正常角度：绘制矩形框
                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                else:
                    # 旋转角度：直接在界面下方显示结果
                    h_frm, w_frm = frame.shape[:2]
                    cv2.putText(frame, f"Found: {text}", (10, h_frm - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            # 简单的过滤：我们假设书籍条码通常是 EAN13
            # 即使不是，我们也先返回，由上层逻辑判断
            if barcode_data:
                found_isbn = barcode_data
                
            # 显示画面
            cv2.imshow('Scan ISBN - Press "q" to cancel', frame)

            # 如果找到了 ISBN，暂停一下给用户视觉确认，然后退出
            if found_isbn:
                print(f"识别成功: {found_isbn}")
                # 绘制最终确认框（绿色实心）
                cv2.waitKey(500) # 停留 0.5 秒
                break

            # 按 'q' 退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return found_isbn

if __name__ == "__main__":
    scanner = BarcodeScanner()
    result = scanner.scan_isbn()
    if result:
        print(f"最终结果: {result}")
    else:
        print("扫描取消或失败")