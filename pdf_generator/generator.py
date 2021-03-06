import os
import shutil
from pathlib import Path

from common_helper_process import execute_shell_command
from pdf_generator.tex_generation.template_engine import (
    LOGO_FILE, MAIN_TEMPLATE, META_TEMPLATE, PLUGIN_TEMPLATE_BLUEPRINT, TemplateEngine
)

PDF_NAME = Path(MAIN_TEMPLATE).with_suffix('.pdf').name


def execute_latex(tmp_dir):
    current_dir = os.getcwd()
    os.chdir(tmp_dir)
    execute_shell_command('env buf_size=1000000 pdflatex {}'.format(MAIN_TEMPLATE))
    os.chdir(current_dir)


def copy_fact_image(target):
    shutil.copy(str(Path(__file__).parent / 'templates' / LOGO_FILE), str(Path(target) / LOGO_FILE))


def render_analysis_templates(engine, analysis):
    return [
        (PLUGIN_TEMPLATE_BLUEPRINT.format(analysis_plugin), engine.render_analysis_template(analysis_plugin, analysis[analysis_plugin])) for analysis_plugin in analysis
    ]


def create_report_filename(meta_data):
    unsafe_name = '{}_analysis_report.pdf'.format(meta_data['device_name'])
    safer_name = unsafe_name.replace(' ', '_').replace('/', '__')
    return safer_name.encode('latin-1', errors='ignore').decode('latin-1')


def compile_pdf(meta_data, tmp_dir):
    copy_fact_image(tmp_dir)
    execute_latex(tmp_dir)
    target_path = Path(tmp_dir, create_report_filename(meta_data))
    shutil.move(str(Path(tmp_dir, PDF_NAME)), str(target_path))
    return target_path


def create_templates(analysis, meta_data, tmp_dir):
    engine = TemplateEngine(tmp_dir=tmp_dir)

    Path(tmp_dir, MAIN_TEMPLATE).write_text(engine.render_main_template(analysis=analysis, meta_data=meta_data))
    Path(tmp_dir, META_TEMPLATE).write_text(engine.render_meta_template(meta_data))

    for filename, rendered_template in render_analysis_templates(engine=engine, analysis=analysis):
        Path(tmp_dir, filename).write_text(rendered_template)
