export const metadata = {
  title: "개인정보 처리방침 | 투자SNS",
  description: "투자SNS 개인정보 처리방침",
};

export default function PrivacyPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">개인정보 처리방침</h1>
      <p className="text-sm text-gray-500 mb-8">시행일: 2026년 3월 15일</p>

      <div className="space-y-8 text-[15px] leading-relaxed text-gray-700">
        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">1. 개인정보의 처리 목적</h2>
          <p>
            투자SNS(이하 &quot;서비스&quot;)는 다음의 목적을 위하여 개인정보를 처리합니다.
            처리하고 있는 개인정보는 다음의 목적 이외의 용도로는 이용되지 않으며,
            이용 목적이 변경되는 경우에는 별도의 동의를 받는 등 필요한 조치를 이행할 예정입니다.
          </p>
          <ul className="list-disc pl-5 mt-2 space-y-1">
            <li>회원 가입 및 관리</li>
            <li>서비스 제공 및 맞춤형 콘텐츠 제공</li>
            <li>투자 시그널 및 리포트 열람 서비스</li>
            <li>서비스 개선 및 통계 분석</li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">2. 수집하는 개인정보 항목</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>필수 항목:</strong> 이메일 주소, 비밀번호(암호화 저장)</li>
            <li><strong>선택 항목:</strong> 닉네임, 프로필 이미지</li>
            <li><strong>자동 수집 항목:</strong> 접속 IP, 접속 일시, 서비스 이용 기록, 쿠키</li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">3. 개인정보의 보유 및 이용 기간</h2>
          <p>
            이용자의 개인정보는 원칙적으로 개인정보의 수집 및 이용 목적이 달성되면 지체 없이 파기합니다.
          </p>
          <ul className="list-disc pl-5 mt-2 space-y-1">
            <li>회원 탈퇴 시: 즉시 파기</li>
            <li>관련 법령에 따른 보존: 계약 또는 청약철회 기록 5년, 접속 기록 3개월</li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">4. 개인정보의 제3자 제공</h2>
          <p>
            서비스는 원칙적으로 이용자의 개인정보를 외부에 제공하지 않습니다.
            다만, 다음의 경우에는 예외로 합니다.
          </p>
          <ul className="list-disc pl-5 mt-2 space-y-1">
            <li>이용자가 사전에 동의한 경우</li>
            <li>법령의 규정에 의거하거나, 수사 목적으로 법령에 정해진 절차와 방법에 따라 수사기관의 요구가 있는 경우</li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">5. 개인정보의 파기 절차 및 방법</h2>
          <p>
            서비스는 개인정보 보유기간의 경과, 처리목적 달성 등 개인정보가 불필요하게 되었을 때에는
            지체 없이 해당 개인정보를 파기합니다.
          </p>
          <ul className="list-disc pl-5 mt-2 space-y-1">
            <li>전자적 파일: 복구 불가능한 방법으로 영구 삭제</li>
            <li>종이 문서: 분쇄기로 분쇄 또는 소각</li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">6. 이용자의 권리와 행사 방법</h2>
          <p>이용자는 언제든지 다음의 권리를 행사할 수 있습니다.</p>
          <ul className="list-disc pl-5 mt-2 space-y-1">
            <li>개인정보 열람 요구</li>
            <li>오류 등이 있을 경우 정정 요구</li>
            <li>삭제 요구</li>
            <li>처리 정지 요구</li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">7. 쿠키의 사용</h2>
          <p>
            서비스는 이용자에게 맞춤형 서비스를 제공하기 위해 쿠키를 사용합니다.
            이용자는 브라우저 설정을 통해 쿠키 저장을 거부할 수 있으며,
            이 경우 일부 서비스 이용에 어려움이 있을 수 있습니다.
          </p>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">8. 개인정보 보호책임자</h2>
          <p>
            서비스는 개인정보 처리에 관한 업무를 총괄해서 책임지고,
            개인정보 처리와 관련한 이용자의 불만처리 및 피해구제 등을 위하여
            아래와 같이 개인정보 보호책임자를 지정하고 있습니다.
          </p>
          <div className="mt-2 p-4 bg-gray-50 rounded-lg">
            <p><strong>개인정보 보호책임자</strong></p>
            <p>이메일: privacy@investsns.com</p>
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">9. 개인정보 처리방침 변경</h2>
          <p>
            이 개인정보 처리방침은 2026년 3월 15일부터 적용됩니다.
            변경사항이 있을 경우 서비스 내 공지사항을 통해 고지할 예정입니다.
          </p>
        </section>
      </div>
    </div>
  );
}
