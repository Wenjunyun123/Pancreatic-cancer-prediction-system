// 页面加载完成后执行
$(document).ready(function() {
    // 回到顶部按钮
    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            $('#back-to-top').fadeIn();
        } else {
            $('#back-to-top').fadeOut();
        }
    });
    
    $('#back-to-top').click(function(e) {
        e.preventDefault();
        $('html, body').animate({scrollTop: 0}, 300);
        return false;
    });

    // 步骤表单导航
    $('.step-item').click(function() {
        const targetStep = $(this).data('step');
        
        // 更新步骤导航激活状态
        $('.step-item').removeClass('active');
        $(this).addClass('active');
        
        // 显示对应步骤的表单
        $('.param-group').removeClass('active');
        $(targetStep).addClass('active');
    });

    // 表单下一步按钮
    $('.btn-next-step').click(function() {
        const currentStep = $(this).closest('.param-group');
        const nextStep = currentStep.next('.param-group');
        const nextStepId = nextStep.attr('id');
        
        // 简单验证当前步骤的表单字段
        let isValid = true;
        currentStep.find('input[required]').each(function() {
            if ($(this).val() === '') {
                isValid = false;
                $(this).addClass('is-invalid');
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        
        if (isValid && nextStep.length) {
            // 更新步骤导航激活状态
            $('.step-item').removeClass('active');
            $(`.step-item[data-step="#${nextStepId}"]`).addClass('active');
            
            // 显示下一步表单
            $('.param-group').removeClass('active');
            nextStep.addClass('active');
            
            // 滚动到表单顶部
            $('html, body').animate({
                scrollTop: $('.steps-container').offset().top - 20
            }, 300);
        }
    });

    // 表单上一步按钮
    $('.btn-prev-step').click(function() {
        const currentStep = $(this).closest('.param-group');
        const prevStep = currentStep.prev('.param-group');
        const prevStepId = prevStep.attr('id');
        
        if (prevStep.length) {
            // 更新步骤导航激活状态
            $('.step-item').removeClass('active');
            $(`.step-item[data-step="#${prevStepId}"]`).addClass('active');
            
            // 显示上一步表单
            $('.param-group').removeClass('active');
            prevStep.addClass('active');
            
            // 滚动到表单顶部
            $('html, body').animate({
                scrollTop: $('.steps-container').offset().top - 20
            }, 300);
        }
    });

    // 表单验证
    $('input[type="text"]').on('input', function() {
        // 验证是否为数字
        const value = $(this).val();
        if (value !== '' && isNaN(value)) {
            $(this).addClass('is-invalid');
            $(this).next('.invalid-feedback').text('请输入有效的数字');
        } else {
            $(this).removeClass('is-invalid');
        }
    });

    // 提交表单前验证并显示加载动画
    $('#prediction-form').submit(function() {
        let isValid = true;
        
        // 验证所有必填字段
        $(this).find('input[required]').each(function() {
            if ($(this).val() === '') {
                isValid = false;
                $(this).addClass('is-invalid');
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        
        if (isValid) {
            // 显示加载动画
            $('#submit-btn').prop('disabled', true);
            $('#submit-btn').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 预测中...');
            return true;
        } else {
            // 滚动到第一个错误字段
            const firstError = $('.is-invalid').first();
            if (firstError.length) {
                const parentGroup = firstError.closest('.param-group');
                const parentGroupId = parentGroup.attr('id');
                
                // 激活包含错误的表单步骤
                $('.param-group').removeClass('active');
                parentGroup.addClass('active');
                
                // 更新步骤导航
                $('.step-item').removeClass('active');
                $(`.step-item[data-step="#${parentGroupId}"]`).addClass('active');
                
                // 滚动到错误字段
                $('html, body').animate({
                    scrollTop: firstError.offset().top - 100
                }, 300);
            }
            return false;
        }
    });

    // 参数提示工具提示初始化
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 如果存在结果图表容器，则初始化图表
    if ($('#result-chart').length) {
        const ctx = document.getElementById('result-chart').getContext('2d');
        
        // 从页面元素获取预测结果数据
        const resultType = $('#result-type').text();
        const benignProb = parseFloat($('#benign-prob').text());
        const malignantProb = parseFloat($('#malignant-prob').text());
        
        // 创建饼图
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['良性', '恶性'],
                datasets: [{
                    data: [benignProb * 100, malignantProb * 100],
                    backgroundColor: [
                        'rgba(107, 208, 152, 0.8)',
                        'rgba(255, 141, 133, 0.8)'
                    ],
                    borderColor: [
                        'rgba(107, 208, 152, 1)',
                        'rgba(255, 141, 133, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${context.raw.toFixed(2)}%`;
                            }
                        }
                    }
                }
            }
        });
        
        // 让概率条动画显示
        setTimeout(function() {
            if (resultType === '良性') {
                $('.probability-value.benign').css('width', `${benignProb * 100}%`);
            } else {
                $('.probability-value.malignant').css('width', `${malignantProb * 100}%`);
            }
        }, 300);
    }
});