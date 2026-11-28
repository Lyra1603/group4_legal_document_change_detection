"""Open the demo in headless Chromium and exercise the user workflow."""
import argparse
from contextlib import contextmanager
import json
import re
from pathlib import Path
import socket
from threading import Thread
from time import monotonic, sleep

from playwright.sync_api import expect, sync_playwright
import uvicorn

from backend.shared_demo import create_app


@contextmanager
def web_server(graph, runtime):
    app = create_app(settings={}, runtime=runtime, document_graph_path=graph)
    server = uvicorn.Server(uvicorn.Config(app, log_level='warning'))
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        listener.listen()
        port = listener.getsockname()[1]
        thread = Thread(target=server.run, kwargs={'sockets': [listener]}, daemon=True)
        thread.start()
        try:
            deadline = monotonic() + 10
            while not server.started and thread.is_alive() and monotonic() < deadline:
                sleep(0.025)
            if not server.started:
                raise RuntimeError('Demo did not start')
            yield f'http://127.0.0.1:{port}/'
        finally:
            server.should_exit = True
            thread.join(timeout=10)


def dot_number(value):
    return f'{value:,}'.replace(',', '.')


def check(page, base, graph):
    path = page.get_by_role('region', name='Đồ thị quan hệ văn bản pháp luật')
    canvas = path.locator('.graph-overview-canvas')
    begin = monotonic()
    page.goto(base)
    nodes, edges = len(graph['nodes']), len(graph['edges'])
    amendments = sum(edge['relation'] == 'AMENDS' for edge in graph['edges'])
    assert nodes and edges and amendments
    all_edges = f'Đang hiện {dot_number(nodes)} nút · {dot_number(edges)} cạnh'
    expect(path.get_by_text(all_edges, exact=True)).to_be_visible()
    # Verify an actual painted Canvas, independently of the status text.
    page.wait_for_function("""
        () => {
          const c = document.querySelector('.graph-overview-canvas');
          const pixels = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
          for (let i = 3; i < pixels.length; i += 4) if (pixels[i]) return true;
          return false;
        }
    """)
    painted_ms = round((monotonic() - begin) * 1000)
    path.get_by_role('button', name='Chỉ hiện nút', exact=True).click()
    path.get_by_role('checkbox', name='Sửa đổi', exact=True).check()
    filtered = f'Đang hiện {dot_number(nodes)} nút · {dot_number(amendments)} / {dot_number(edges)} cạnh đang hiện'
    expect(path.get_by_text(filtered, exact=True)).to_be_visible()
    path.get_by_role('button', name='Hiện tất cả cạnh', exact=True).click()
    expect(path.get_by_text(all_edges, exact=True)).to_be_visible()
    path.get_by_role('button', name='Phóng to', exact=True).click()
    expect(path.get_by_text('140%', exact=True)).to_be_visible()
    expect(canvas).to_be_visible()
    path.get_by_role('button', name='Vừa khung', exact=True).click()
    expect(path.get_by_text('100%', exact=True)).to_be_visible()
    path.get_by_label('Tìm theo số hiệu hoặc tên văn bản').fill('08/2014/TT-BTP')
    path.get_by_role('button', name='Tìm văn bản', exact=True).click()
    path.locator('.graph-results').get_by_role(
        'button', name=re.compile(r'^08\/2014\/TT-BTP ·')).click()
    path.get_by_role('button', name='Xem bằng chứng quanh nút').click()
    path.get_by_role('button', name='Sửa đổi · 05/2011/TT-BTP', exact=True).press('Enter')
    expect(path.locator('.graph-evidence')).to_contain_text('dataset:56666 · block:22')
    expect(path.locator('.graph-evidence')).to_contain_text('1. Sửa đổi khoản 2 Điều 2 như sau:')

    page.get_by_label('Chọn bộ dữ liệu mẫu').select_option('case_02')
    page.get_by_role('button', name='Nạp file mẫu', exact=False).click()
    page.get_by_role('button', name='Tìm văn bản gốc', exact=True).click()
    expect(page.get_by_role('heading', name='Báo cáo đối chiếu')).to_be_visible()
    expect(page.locator('#report-items')).to_contain_text('Khoản 5 Điều 16')
    return dict(nodes=nodes, edges=edges, first_paint_ms=painted_ms,
                sample_s='case_02', verified_source='dataset:56666 · block:22')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--graph-file', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    graph = json.loads(args.graph_file.read_text(encoding='utf-8'))
    with web_server(args.graph_file, args.output_dir / 'runtime') as base, sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context()
        context.tracing.start(screenshots=True, snapshots=True)
        page = context.new_page()
        page_errors = []
        page.on('pageerror', lambda error: page_errors.append(str(error)))
        try:
            result = check(page, base, graph)
            if page_errors:
                raise AssertionError(page_errors)
        except Exception:
            page.screenshot(path=args.output_dir / 'failure.png', full_page=True)
            context.tracing.stop(path=args.output_dir / 'trace.zip')
            raise
        else:
            context.tracing.stop()
            summary = json.dumps(result, ensure_ascii=False)
            (args.output_dir / 'web-summary.json').write_text(summary + '\n', encoding='utf-8')
            print(summary)
        finally:
            browser.close()


if __name__ == '__main__':
    main()
